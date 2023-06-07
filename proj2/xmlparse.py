#
# Author: Andrej Nešpor
# Login: xnespo10
#

import xml.etree.ElementTree as ET
import sys
import re
from operator import itemgetter

from errors import Exits as err
from instructions import *

# Class to validate XML source input using ElementTree
class Xmlparser:
    def __init__(self, input):
        self.input = input
        self.orders = []
        self.program = []
        self.known = Instructions('')

    def parse(self):

        # Start XML validation
        try:
            root = ET.fromstring(self.input.read())
        except ET.ParseError as e:
            print("Error:", e, file=sys.stderr)
            sys.exit(err.xml_file)

        self.validate_header(root)

        self.check_inst(root)

        self.sort()
        self.rewrite()


    # Check XML header
    def validate_header(self, root):
        if root.tag != 'program' or root.get('language').lower() != 'ippcode23':
            print("Wrong header", root.tag, root.get('language'), file=sys.stderr)
            sys.exit(err.xml_syntax)

    # Check each instruction
    def check_inst(self, root):
        for instruction in root:

            if instruction.tag != 'instruction':
                print("Bad arg:", instruction.tag, file=sys.stderr)
                sys.exit(err.xml_syntax)

            attrs = []
            order = instruction.get('order', '-1')
            opcode = instruction.get('opcode', '1').upper()

            # Check if opcode is number -> error
            if opcode.isnumeric():
                print("Bad opcode", opcode, file=sys.stderr)
                sys.exit(err.xml_syntax)

            # Sort arguments of instruction
            try:
                instruction[:] = sorted(instruction, key=lambda arg: int(arg.tag[3:]))
            except ValueError as e:
                print("Error:", e, file=sys.stderr)
                sys.exit(err.xml_syntax)

            if not order.isnumeric() or not opcode:
                print("Bad order, missing order or missing opcode", order, opcode, file=sys.stderr)
                sys.exit(err.xml_syntax)

            order = int(order)
            if order == 0:
                print('Zero order', file=sys.stderr)
                sys.exit(err.xml_syntax)

            if order in self.orders:
                print('Duplicate order', file=sys.stderr)
                sys.exit(err.xml_syntax)
            else:
                self.orders.append(order)

            # Check if opcode is known by ippcode23
            self.check_opcode(opcode)

            arg_num = self.known.instructions[opcode]['args']

            if len(instruction) != arg_num:
                print("Too little arguments:", len(instruction), file=sys.stderr)
                sys.exit(err.xml_syntax)

            # Append to instruction
            attrs.append(order)
            attrs.append(opcode)

            # Check arguments
            self.check_args(instruction, attrs, arg_num)

            self.program.append(attrs)

    # Check if opcode is known by ippcode23
    def check_opcode(self, opcode):
        check = False
        for inst in self.known.instructions:
            if opcode == inst:
                check = True
        if not check:
            print("Unkown opcode:", opcode, file=sys.stderr)
            sys.exit(err.xml_syntax)

    # Check all args of instruction
    def check_args(self, instruction, attrs, args):
        for arg in instruction:
            if arg.tag[:-1] != 'arg' or int(arg.tag[3:]) > args:
                print("Bad arg:", arg.tag, file=sys.stderr)
                sys.exit(err.xml_syntax)

            arg_type = arg.get('type').lower()

            try:
                arg_value = arg.text.strip()
            except AttributeError:
                arg_value = ''

            if not arg_type:
                print("Missing type", file=sys.stderr)
                sys.exit(err.xml_syntax)

            if instruction.get('opcode').upper() == 'READ' and arg.tag[3:] == '2':
                if arg_type != 'type':
                    print("Wrong read argument", file=sys.stderr)
                    sys.exit(err.xml_syntax)

            # Check if value corresponds with type
            if arg_type == 'string':
                arg_type = 'str'
                arg_value = re.sub(r'\\(\d{3})', lambda x: chr(int(x.group(1))), arg_value)
            elif arg_type == 'int':
                if not arg_value.isnumeric():
                    # Convert signed int from string
                    arg_value = arg_value.split('-', 1)
                    if arg_value[0] == '' and arg_value[1].isnumeric():
                        arg_value = int(arg_value[1]) * -1
                    else:
                        print("Missing type", file=sys.stderr)
                        sys.exit(err.xml_syntax)
                else:
                    arg_value = int(arg_value)
            elif arg_type == 'bool':
                if arg_value.lower() != 'true':
                    arg_value = 'false'
                else:
                    arg_value = arg_value.lower()
            elif arg_type == 'type':
                if arg_value.lower() == 'int' or arg_value.lower() == 'string' or arg_value.lower() == 'bool':
                    arg_value = arg_value.lower()
                else:
                    print("Wrong type value", file=sys.stderr)
                    sys.exit(err.xml_syntax)
            elif arg_type == 'var':
                # Check valid frames
                if arg_value[:2] != 'GF' and arg_value[:2] != 'LF' and arg_value[:2] != 'TF':
                    print("Wrong frame in variable name", file=sys.stderr)
                    sys.exit(err.xml_syntax)

            # Append to instruction
            attrs.append(arg_type)
            attrs.append(arg_value)

    # Sort list of all instructions by order
    def sort(self):
        self.program.sort(key=itemgetter(0))

    # Remove order in each instruction
    def rewrite(self):
        for inst in self.program:
            inst.pop(0)
