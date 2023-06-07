#
# Author: Andrej Nešpor
# Login: xnespo10
#

import argparse
import sys

from errors import Exits as err

# Class for parsing arguments using argparse
class Argsparse:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='IPPcode23 Interpreter', add_help=False)
        self.parser.add_argument('--source')
        self.parser.add_argument('--input')
        self.args, self.rem_args = self.parser.parse_known_args()
        self.source = ''
        self.input = ''

    # Function that parses the arguments
    def parse(self):
        if '--help' in self.rem_args:
            # If there is help argument, there can't be any other
            if len(self.rem_args) > 1 or (self.args.input or self.args.source):
                sys.exit(err.param)
            else:
                self.print_help()
                sys.exit(0)

        if not self.args.source and not self.args.input:
            # At least one of source and input files is required
            print("Both args missing", file=sys.stderr)
            sys.exit(1)

        # 
        if self.args.source:
            try:
                self.source = open(self.args.source)
            except:
                print("Error opening file", file=sys.stderr)
                sys.exit(err.in_file)
        else:
            self.source = sys.stdin

        if self.args.input:
            try:
                self.input = open(self.args.input)
            except:
                print("Error opening file", file=sys.stderr)
                sys.exit(err.in_file)
        else:
            self.input = 'false'

    # Help message
    def print_help(self):
        print('Usage: interpreter.py [--help] [--source=SOURCE] [--input=INPUT]\n')
        print('IPPcode23 Interpreter\n')
        print('options:\n')
        print('--help, -h           show this help message and exit')
        print('--source=, --source  Input file with XML representation of IPPcode23 code')
        print('--input=, --input    Input file with inputs for the READ instruction')
