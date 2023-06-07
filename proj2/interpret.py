#
# Author: Andrej Nešpor
# Login: xnespo10
#


#------     IMPORT CLASSES      -------#
from xmlparse import *
from argsparse import *
from instructions import *
#--------------------------------------#

def main():
    args = Argsparse()
    args.parse()

    #print('Test: ', args.source.name, file=sys.stderr)

    xml = Xmlparser(args.source)
    xml.parse()

    run = Instructions(args.input)
    run.handle_instructions(xml.program)

    return

if __name__ == '__main__':
    main()
