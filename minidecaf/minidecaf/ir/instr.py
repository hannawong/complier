from ..utils import *

class IRInstr:
    pass

class Const(IRInstr):
    def __init__(self, v:int):
        assert MIN_INT < v < MAX_INT
        self.v = v

    def accept(self, visitor):
        visitor.visitConst(self)


class Ret(IRInstr):
    def accept(self, visitor):
        visitor.visitRet()


class Unary(IRInstr):
    def __init__(self, op:str):
        assert op in unaryOps
        self.op = op

    def accept(self, visitor):
        visitor.visitUnary(self)


class Binary(IRInstr):
    def __init__(self, op:str):
        assert op in binaryOps
        self.op = op

    def accept(self, visitor):
        visitor.visitBinary(self)

class Pop(IRInstr):
    def accept(self, visitor):
        visitor.visitPop()


class Load(IRInstr):
    def accept(self, visitor):
        visitor.visitLoad()


class Store(IRInstr):
    def accept(self, visitor):
        visitor.visitStore()


class Label(IRInstr):
    def __init__(self, label:str):
        self.label = label

    def accept(self, visitor):
        visitor.visitLabel(self)


class Branch(IRInstr):
    def __init__(self, op, label):
        assert op in branchOps
        self.op = op
        self.label = label

    def accept(self, visitor):
        visitor.visitBranch(self)


class FrameSlot(IRInstr):
    def __init__(self, fpOffset:int):
        assert fpOffset < 0
        self.offset = fpOffset

    def accept(self, visitor):
        visitor.visitFrameSlot(self)


class GlobalSymbol(IRInstr):
    def __init__(self, sym:str):
        self.sym = sym

    def accept(self, visitor):
        visitor.visitGlobalSymbol(self)


class Call(IRInstr):
    def __init__(self, func:str):
        self.func = func

    def accept(self, visitor):
        visitor.visitCall(self)

