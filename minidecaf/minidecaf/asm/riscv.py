from ..utils import *
from ..ir.instr import *
from ..ir import *
from . import *

def _push(val):
    if type(val) is int:
        return ["addi sp, sp, -4", "li t1, "+str(val), "sw t1, 0(sp)"] # push int
    else:
        return ["addi sp, sp, -4", "sw "+str(val)+", 0(sp)"] # push register

def push(*regs): ###several pushes
    list=[]
    for i in regs:
        list+=_push(i)
    return list


def _pop(reg):
    list=[]
    if reg is not None:
        list.append("lw "+str(reg)+", 0(sp)")
    list.append("addi sp, sp, 4")
    return list

def pop(*regs):
    list=[]
    for i in regs:
        list+=_pop(i)
    return list

unarydic={'-': "neg", '!': "seqz", '~': "not"}
def unary(op):
    op =unarydic[op]
    return pop("t1") + [op+" t1, t1"] + push("t1")

arithdic = { "+": "add", "-": "sub", "*": "mul", "/": "div", "%": "rem" }
equaldic = { "==": "seqz", "!=": "snez" }
compdic = { "<": "slt", ">": "sgt" }
def binary(op):
    if op in arithdic:
        return pop("t2", "t1") + [arithdic[op]+" t1, t1, t2"] + push("t1")
    if op in equaldic:
        return pop("t2", "t1") + ["sub t1, t1, t2", equaldic[op]+" t1, t1"] + push("t1")
    if op in compdic:
        return pop("t2", "t1") + [compdic[op]+" t1, t1, t2"] + push("t1")
    if op == "||":
        return pop("t2", "t1") + ["or t1, t1, t2", "snez t1, t1"] + push("t1")
    if op == "&&":
        return pop("t2") + unary("!") + push("t2") + unary("!") + binary("||") + unary("!")
    if op == "<=":
        return binary(">") + unary("!")
    if op == ">=":
        return binary("<") + unary("!")

def frameSlot(offset):
    return push("fp", offset) + binary("+")

def load():
    return pop("t1") + ["lw t1, 0(t1)"] + push("t1")

def store():
    return pop("t2", "t1") + ["sw t1, 0(t2)"] + push("t1")


def ret(func:str):
    return ["beqz x0, "+func+"_exit"]


def branch(op, label:str):
    b1 = { "br": (2, "beq"), "beqz": (1, "beq"), "bnez": (1, "bne") }
    if op in b1:
        naux, op = b1[op]
        return push(*[0]*naux) + branch(op, label)
    return pop("t2", "t1") + [f"{op} t1, t2, {label}"]


def label(label:str):
    return [f"{label}:"]


def call(func:str, nParam:int):
    return [f"call {func}"] + pop(*[None]*nParam) + push("a0")


def globalSymbol(sym:str):
    return [f"la t1, {sym}"] + push("t1")

class RISCVAsmGen():
    def __init__(self, emitter):
        self._E = emitter
        self.curFunc = None
        self.curParamInfo = None

    def visitRet(self):
        self._E(ret(self.curFunc))

    def visitConst(self, instr):
        self._E(push(instr.v))

    def visitUnary(self, instr):
        self._E(unary(instr.op))

    def visitBinary(self, instr):
        self._E(binary(instr.op))

    def visitFrameSlot(self,instr):
        self._E(frameSlot(instr.offset))

    def visitLoad(self):
        self._E(load())

    def visitStore(self,):
        self._E(store())

    def visitPop(self):
        self._E(pop(None))

    def visitBranch(self, instr):
        self._E(branch(instr.op, instr.label))

    def visitLabel(self, instr):
        self._E(label(instr.label))

    def visitCall(self, instr:Call):
        func=None
        for v in self.ir.funcs:
            if instr.func == v.name:
                func=v
        self._E(call(func.name, func.nParams))

    def visitGlobalSymbol(self, instr):
        self._E(globalSymbol(instr.sym))

    def genPrologue(self, func:IRFunc):
        self._E([
            "\t.text",
            f"\t.globl {func.name}",
            func.name+":"] +
            push("ra", "fp") + [
            "\tmv fp, sp"
            ])

        for i in range(func.nParams):
            fr, to = INT_BYTES*(i+2), -INT_BYTES*(i+1)
            self._E([
                f"\tlw t1, {fr}(fp)"] +
                push("t1"))

    def genEpilogue(self, func:IRFunc):
        self._E(
            push(0) + [
            f"{func.name}_exit:",
            "\tlw a0, 0(sp)",
            "\tmv sp, fp" ]+
            pop("fp", "ra") + [
            "\tjr ra"])

    def genFunc(self, func:IRFunc):
        self.curFunc = func.name
        self.genPrologue(func)
        for instr in func.instrs:
            instr.accept(self)
        self.genEpilogue(func)

    def genGlob(self, glob:IRGlob):
        if glob.init is None:
            self._E([f"\t.comm {glob.sym},{glob.size},{glob.align}"])
        else:
            self._E([
                "\t.data",
                f"\t.globl {glob.sym}",
                f"\t.align {glob.align}",
                f"\t.size {glob.sym}, {glob.size}",
                f"{glob.sym}:",
                f"\t.quad {glob.init}"])

    def gen(self, ir):
        self.ir = ir
        for glob in ir.globs:
            self.genGlob(glob)
        for func in ir.funcs:
            self.genFunc(func)

