from ..utils import *
from ..generated.MiniDecafParser import MiniDecafParser
from ..generated.MiniDecafVisitor import MiniDecafVisitor


class Variable:  ###variable name info
    _varcnt = {}
    def __init__(self, ident, offset,size=4):
        if ident not in self._varcnt:
            self._varcnt[ident] = 0
        else:
            self._varcnt[ident] += 1
        self.ident = ident  ##name
        self.offset = offset  ##-4,-8
        self.size = size
        self.id = self._varcnt[ident]

    def __eq__(self, other):
        return self.id == other.id and self.ident == other.ident and self.offset == other.offset and self.size==other.size

    def __hash__(self):
        return hash((self.ident, self.id, self.offset,self.size))


class FuncNameInfo:
    def __init__(self, hasDef=True):
        self._v = {}    # term -> Variable
        self._pos = {}  # term -> (int, int)
        self.blockSlots = {} # BlockContext / ForDeclStmtContext -> int >= 0
        self.hasDef = hasDef

    def bind(self, term, var, pos):
        self._v[term] = var
        self._pos[term] = pos


    def __getitem__(self, term):
        return self._v[term]


class GlobInfo:
    def __init__(self, var:Variable, size:int, init=None):
        self.var = var
        self.size = var.size
        self.init = init # not a byte array -- that requires endian info



class NameInfo:
    def __init__(self):
        self.funcs = {} # str -> FuncNameInfo. Initialized by Def.
        self.globs = {} # str -> GlobInfo.
        self._v = {}

    def freeze(self):
        for funcNameInfo in self.funcs.values():
            self._v.update(funcNameInfo._v)

    def __getitem__(self, ctx):
        return self._v[ctx]



class stacked_dict:
    def __init__(self):
        self._s = [{}]
        self._d = [{}]

    def __getitem__(self, key):
        return self._s[-1][key]

    def __setitem__(self, key, value):
        self._d[-1][key] = self._s[-1][key] = value

    def __len__(self):
        return len(self._s[-1])

    def push(self):
        self._s.append(deepcopy(self._s[-1]))
        self._d.append({})

    def pop(self):
        assert len(self._s) > 1
        self._s.pop()
        self._d.pop()

    #def peek(self, last=0):
        #return self._d[-1-last]

class Namer(MiniDecafVisitor):
    def __init__(self):
        self._v = stacked_dict() # str -> Variable
        self._nSlots = [] # number of frame slots on block entry
        self.curNSlots = 0
        self.nameInfo = NameInfo()
        self._curFuncNameInfo = None # == self.nameInfo[curFunc]

    def defVar(self, ctx, term, numInts=1): ##define variable
        self.curNSlots += numInts
        var = Variable(text(term),-4 * self.curNSlots, 4 * numInts)  ###name,offset, size
        self._v[text(term)] = var
        pos = (ctx.start.line, ctx.start.column)
        self._curFuncNameInfo.bind(term, var, pos)

    def useVar(self, ctx, term):
        var = self._v[text(term)]
        pos = (ctx.start.line, ctx.start.column)
        self._curFuncNameInfo.bind(term, var, pos)

    def declNElems(self, ctx:MiniDecafParser.DeclContext): ##how many elements did u declare
        res = prod([int(text(x)) for x in ctx.Integer()])
        assert 0 < res < MAX_INT
        return res

    def enterScope(self, ctx):
        self._v.push()
        self._nSlots.append(self.curNSlots)

    def exitScope(self, ctx):
        self._curFuncNameInfo.blockSlots[ctx] = self.curNSlots - self._nSlots[-1]
        self.curNSlots = self._nSlots[-1]
        self._v.pop()
        self._nSlots.pop()

    def visitBlock(self, ctx:MiniDecafParser.BlockContext):
        self.enterScope(ctx)
        self.visitChildren(ctx)
        self.exitScope(ctx)

    def visitDecl(self, ctx:MiniDecafParser.DeclContext):  ##declare
        num=self.declNElems(ctx)
        if ctx.expr() is not None:
            ctx.expr().accept(self)
        var = text(ctx.Ident())
        assert var not in self._v._d[-1] ##not redeclaration
        self.defVar(ctx, ctx.Ident(), num)

    def visitAtomIdent(self, ctx:MiniDecafParser.AtomIdentContext):  ###visit variable
        var = text(ctx.Ident())
        assert var in self._v._s[-1].keys()  ##visit variable
        self.useVar(ctx, ctx.Ident())

    def visitForDeclStmt(self, ctx:MiniDecafParser.ForDeclStmtContext):
        self.enterScope(ctx)
        self.visitChildren(ctx)
        self.exitScope(ctx)


    def visitProg(self, ctx:MiniDecafParser.ProgContext):
        self.visitChildren(ctx)
        self.nameInfo.freeze()

    def visitFuncDef(self, ctx:MiniDecafParser.FuncDefContext):
        func = text(ctx.Ident())
        if func in self.nameInfo.funcs and\
                self.nameInfo.funcs[func].hasDef:
            raise MiniDecafError(f"redefinition of function {func}")
        funcNameInfo = FuncNameInfo(hasDef=True)
        self._curFuncNameInfo = self.nameInfo.funcs[func] = funcNameInfo
        self.enterScope(ctx.block())
        ctx.paramList().accept(self)
        self.visitChildren(ctx.block())
        self.exitScope(ctx.block())
        self._curFuncNameInfo = None

    def visitFuncDecl(self, ctx:MiniDecafParser.FuncDeclContext):
        func = text(ctx.Ident())
        if func in self.nameInfo.globs:
            raise MiniDecafError(ctx, f"global variable {func} redeclared as function")
        funcNameInfo = FuncNameInfo(hasDef=False)
        if func not in self.nameInfo.funcs:
            self.nameInfo.funcs[func] = funcNameInfo

    def globalInitializer(self, ctx:MiniDecafParser.ExprContext):
        if ctx is None:
            return None
        try:
            initializer = safeEval(text(ctx))
            return initializer
        except:
            raise MiniDecafError(ctx, "global initializers must be constants")

    def visitDeclExternalDecl(self, ctx:MiniDecafParser.DeclExternalDeclContext):
        ctx = ctx.decl()
        init = self.globalInitializer(ctx.expr())
        varStr = text(ctx.Ident())
        if varStr in self.nameInfo.funcs:
            raise MiniDecafError(ctx, f"function {varStr} redeclared as global variable")
        var = Variable(varStr, None, INT_BYTES * self.declNElems(ctx))
        globInfo = GlobInfo(var, INT_BYTES, init)
        if varStr in self._v._d[-1]:
            prevGlobInfo = self.nameInfo.globs[varStr]
            if prevGlobInfo.init is not None and globInfo.init is not None:
                raise MiniDecafError(ctx, f"redefinition of variable {varStr}")
            if globInfo.init is not None:
                self.nameInfo.globs[varStr].init = init
        else:
            self._v[varStr] = var
            self.nameInfo.globs[varStr] = globInfo

