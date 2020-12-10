import sys
from copy import deepcopy

INT_BYTES = 4

MAX_INT = 2**(INT_BYTES*8-1) - 1
MIN_INT = -2**(INT_BYTES*8)

class BailErrorListener:
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise MiniDecafError()

class MiniDecafError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)



def text(x):
    if type(x) is str:
        return x
    if x is not None:
        return str(x.getText())



def noOp(*args, **kwargs):
    pass


def safeEval(s:str):
    from ast import literal_eval
    return literal_eval(s)

def prod(l):
    s = 1
    for i in l:
        s *= i
    return s

def expandIterableKey(d:list):
    d2 = {}
    for (keys, val) in d:
        for key in keys:
            d2[key] = val
    return d2

unaryOps = ['-', '!', '~', '&', '*']
unaryOpStrs = ["neg", 'lnot', "not", "addrof", "deref"]


arithOps = ['+', '-', '*', '/', '%']
eqOps = ["==", "!="]
relOps = ["<", "<=", ">", ">="]
logicOps = ["&&", "||"]
binaryOps = ['+', '-', '*', '/', '%', "==", "!=", "<", "<=", ">", ">=", "&&", "||"]
binaryOpStrs = ["add", "sub", "mul", "div", "rem", "eq", "ne", "lt", "le", "gt", "ge", "land", "lor"]
strOfBinaryOp = {o: s for (o, s) in zip(binaryOps, binaryOpStrs)}

branchOps = ["br", "beqz", "bnez", "beq", "bne"]


