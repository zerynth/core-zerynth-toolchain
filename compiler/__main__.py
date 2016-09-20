#!/usr/bin/python

import os
import sys
import getopt
import pickle
import json


# SET CURRENT DIR
CURRENT_DIR = os.path.dirname(__file__)
aa, bb = os.path.split(os.path.abspath(CURRENT_DIR))
sys.path[0] = aa

from compiler.astwalker import AstWalker
from compiler.compiler import Compiler
from compiler.utils.code import CodeRepr


def main(argv):
    print("#### Zerynth VM Compiler - 1.0.0")
    print("")
    inputfile = ''
    outputfile = 'viper.out'
    asmon = 0
    asfile = 'tests/testcode.h'
    try:
        opts, args = getopt.getopt(argv, "hi:o:c", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print('compile -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('compile -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-c"):
            asmon = 1

    cmpl = Compiler(inputfile)

    try:
        bar, rep, co = cmpl.compile()
    except Exception as e:
        print("Compile errors!!",e)
        raise e
        sys.exit(2)

    with open(outputfile, "w") as out:        
        out.write(json.dumps(bar))
    with open(outputfile+".vpd", "wb") as out:
        pickle.dump(rep,out)

    if asmon:
        res = []
        with open(asfile, "wb") as out:

            res.append('const uint8_t codearea[] STORED ={')
            for b in bar:
                res.append(str(b))
                res.append(",")
            res.pop()
            res.append("};")
            out.write(bytes("".join(res), "UTF-8"))


if __name__ == "__main__":
    main(sys.argv[1:])
