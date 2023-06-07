#
# Author: Andrej Nešpor
# Login: xnespo10
#

import sys

from runtime import *
from errors import Exits as err


# Class that runs the interpret by going through list of all instructions
# and calling instruction methods

# Also used in Xmlparser class to check if found opcodes are known by ippcode23
# and number of arguments is correct
class Instructions:
    def __init__(self, input):
        self.input = input
        # Runtime class instance because runtime needs all labels and positions
        self.runtime = Runtime(self.input)
        self.instructions = {
            'MOVE': {'func': self.runtime._move, 'args': 2},
            'CREATEFRAME': {'func': self.runtime._createframe, 'args': 0},
            'PUSHFRAME': {'func': self.runtime._pushframe, 'args': 0},
            'POPFRAME': {'func': self.runtime._popframe, 'args': 0},
            'DEFVAR': {'func': self.runtime._defvar, 'args': 1},
            'CALL': {'func': self.runtime._jumps, 'args': 1},
            'RETURN': {'func': self.runtime._return, 'args': 0},
            'PUSHS': {'func': self.runtime._pushs, 'args': 1},
            'POPS': {'func': self.runtime._pops, 'args': 1},
            'ADD': {'func': self.runtime._numeric, 'args': 3},
            'SUB': {'func': self.runtime._numeric, 'args': 3},
            'MUL': {'func': self.runtime._numeric, 'args': 3},
            'IDIV': {'func': self.runtime._numeric, 'args': 3},
            'LT': {'func': self.runtime._LT, 'args': 3},
            'GT': {'func': self.runtime._GT, 'args': 3},
            'EQ': {'func': self.runtime._EQ, 'args': 3},
            'AND': {'func': self.runtime._logic, 'args': 3},
            'OR': {'func': self.runtime._logic, 'args': 3},
            'NOT': {'func': self.runtime._not, 'args': 2},
            'INT2CHAR': {'func': self.runtime._int2char, 'args': 2},
            'STRI2INT': {'func': self.runtime._stri2int, 'args': 3},
            'READ': {'func': self.runtime._read, 'args': 2},
            'WRITE': {'func': self.runtime._write, 'args': 1},
            'CONCAT': {'func': self.runtime._concat, 'args': 3},
            'STRLEN': {'func': self.runtime._strlen, 'args': 2},
            'GETCHAR': {'func': self.runtime._getchar, 'args': 3},
            'SETCHAR': {'func': self.runtime._setchar, 'args': 3},
            'TYPE': {'func': self.runtime._type, 'args': 2},
            'LABEL': {'func': self.runtime._label, 'args': 1},
            'JUMP': {'func': self.runtime._jumps, 'args': 1},
            'JUMPIFEQ': {'func': self.runtime._jumps, 'args': 3},
            'JUMPIFNEQ': {'func': self.runtime._jumps, 'args': 3},
            'EXIT': {'func': self.runtime._exit, 'args': 1},
            'DPRINT': {'func': self.runtime._dprint, 'args': 1},
            'BREAK': {'func': self.runtime._break, 'args': 0},
        }

    def handle_instructions(self, instructions):
        i = 1
        # Iterate through program instructions to find all labels
        for instr in instructions:
            if instr[0] == 'LABEL':
                if instr[2] in self.runtime.labels:
                    print('Redefining label', file=sys.stderr)
                    sys.exit(err.semantic)
                else:
                    self.runtime.labels[instr[2]] = i
            i += 1

        i = 0
        # Iterate through program instructions to execute all instructions
        while i < len(instructions):
            if instructions[i][0] in self.instructions:
                instruction = self.instructions[instructions[i][0]]
                instruction['func'](instructions[i], i+1)
            if self.runtime.position != -1:
                i = self.runtime.position
                self.runtime.position = -1
            else:
                i += 1
