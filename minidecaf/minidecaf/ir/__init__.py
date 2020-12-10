from ..utils import *
#from .instr import IRInstr
#from .visitor import IRVisitor


class IRFunc:  ##function IR
    def __init__(self, name:str, nParams:int, instrs):
        self.name = name  ##name of function
        self.nParams = nParams ##number of parameters
        self.instrs = instrs


class IRGlob:  #global value
    def __init__(self, sym:str, size:int, init=None, align=INT_BYTES):
        self.sym = sym  #name
        self.size = size #int:4
        self.init = init #the value
        self.align = align
        #print(self.sym," size:",self.size," init:",self.init," align:",self.align)


class IRProg:  ##the overall program
    def __init__(self, funcs:[IRFunc], globs:[IRGlob]):
        self.funcs = funcs ##every functions, a list
        self.globs = globs ##every globals, a list

