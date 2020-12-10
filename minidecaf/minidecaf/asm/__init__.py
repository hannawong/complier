from .riscv import RISCVAsmGen as AsmGen


def asmGen(ir, fout):  #ir:IRProg
    asmEmitter = AsmEmitter(fout)
    AsmGen(asmEmitter).gen(ir)


class AsmEmitter:
    def __init__(self, fout):
        self.f = fout

    def __call__(self, coms):
        for com in coms:
            print(com, file=self.f)
