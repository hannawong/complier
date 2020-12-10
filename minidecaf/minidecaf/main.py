import sys
import argparse
from antlr4 import *


from .generated.MiniDecafLexer import MiniDecafLexer
from .generated.MiniDecafParser import MiniDecafParser
from .asm import asmGen
from .frontend import irGen, nameGen, typeCheck
from .utils import *


def parseArgs(): ###arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("infile")
    return parser.parse_args()

def Lexer(inputStream): ###step1:lexer
    lexer = MiniDecafLexer(inputStream)
    lexer.addErrorListener(BailErrorListener())
    return CommonTokenStream(lexer)

def Parser(tokenStream):  ##step2: parser
    parser = MiniDecafParser(tokenStream)
    parser._errHandler = BailErrorStrategy()
    tree = parser.prog()
    return tree

def IRGen(tree, nameInfo, typeInfo):
    ir = irGen(tree, nameInfo, typeInfo)
    return ir


def AsmGen(ir, outfile):
    out=open(outfile,"w")
    asmGen(ir,out)




def main(argv):
    #try:
        global args
        args = parseArgs()
        inputStream = FileStream(args.infile)  ###character stream, the initial code
        tokenStream = Lexer(inputStream)
        tree = Parser(tokenStream)
        nameInfo = nameGen(tree)
        typeInfo = typeCheck(tree, nameInfo)
        ir = IRGen(tree, nameInfo, typeInfo)
        outfile=args.infile[0:-2]+".s"
        AsmGen(ir,outfile)
        code=open(outfile).read()
        print(code)
        return 0
    #except MiniDecafError as e:
        #print(e, file=sys.stderr)
        #return 1
