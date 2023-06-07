#
# Author: Andrej Nešpor
# Login: xnespo10
#

import sys

from errors import Exits as err

# Class where frames, label_list and all instructions are implemented
class Runtime:
    def __init__(self, input):
        self.input = input
        self.position = -1
        self.labels = {}
        self.position_stack = []
        self.data_stack = []
        self._GF = {}
        # LF is a list of Temporary frames
        self._LF = []
        self._TF = {}
        self._TFcreated = False;

    # Returns frame, None if there's no frame to be returned
    def getFrame(self, frame):
        if frame == 'GF':
            return self._GF
        elif frame == 'LF':
            return (self._LF[0] if len(self._LF) > 0 else None)
        elif frame == 'TF':
            return (self._TF if self._TFcreated else None)
        else:
            return None
    
    # Returns values from arguments
    def getValues(self, var, data, type):
        if not var is None:
            frame, var = self.split_var(var)
            Frame = self.getFrame(frame)
            if Frame is None:
                print('Frame not created', file=sys.stderr)
                sys.exit(err.unknown_frame)
            else:
                if var not in Frame:
                    print('Accesing non-existing promenna', file=sys.stderr)
                    sys.exit(err.unknown_var)
                elif Frame[var]['type'] == None and Frame[var]['data'] == None:
                    print('Accesing non-inicialized promenna', file=sys.stderr)
                    sys.exit(err.unknown_value)
                else:
                    return Frame[var]['data'], Frame[var]['type']
        if not (data is None) or not (type is None):
            return data, type

    # Returns argument data and types if instruction has 3 arguments
    def triargs(self, instr):
        if instr[3] == 'var':
            data1, type1 = self.getValues(instr[4], None, None)
        else:
            data1, type1 = self.getValues(None, instr[4],instr[3])
        if instr[5] == 'var':
            data2, type2 = self.getValues(instr[6], None, None)
        else:
            data2, type2 = self.getValues(None, instr[6],instr[5])

        return data1, type1, data2, type2
    
    # Returns argument data and types if instruction has 2 arguments
    def dualargs(self, instr):
        if instr[3] == 'var':
            data1, type1 = self.getValues(instr[4], None, None)
        else:
            data1, type1 = self.getValues(None, instr[4],instr[3])

        return data1, type1
    
    # Returns argument data and types if instruction has 1 argument
    def varargs(self, instr):
        if instr[1] == 'var':
            data1, type1 = self.getValues(instr[2], None, None)
        else:
            data1, type1 = self.getValues(None, instr[2],instr[1])

        return data1, type1

    # Split variable name by @
    def split_var(self, instr):
        return instr.split('@', 1)
    

    #
    # Functions implementing each instructions
    #

    def _createframe(self, instr, where):
        self._TFcreated = True
        self._TF = {}

    def _pushframe(self, instr, where):
        if self._TFcreated:
            self._LF.insert(0, self._TF)
            self._TFcreated = False
            self._TF = {}
        else:
            print('Unknown frame', file=sys.stderr)
            sys.exit(err.unknown_frame)

    def _popframe(self, instr, where):
        if not self._LF:
            print('Popping nonexisting frame', file=sys.stderr)
            sys.exit(err.unknown_frame)
        
        self._TF = self._LF.pop(0)
        self._TFcreated = True

    def _defvar(self, instr, where):
        frame, var = self.split_var(instr[2])
        Frame = self.getFrame(frame)
        if Frame is None:
            print('Frame not created _defvar', file=sys.stderr)
            sys.exit(err.unknown_frame)
        else:
            if var in Frame:
                print('Creating existing variable', file=sys.stderr)
                sys.exit(err.semantic)
            else:
                Frame[var] = {'type': None, 'data': None}


    # Not only int MOVE instruction
    # but also every time any instruction has to save it's result
    def _move(self, instr, where):
        first_frame, first_var = self.split_var(instr[2])
        firstFrame = self.getFrame(first_frame)
        # Check if frame exists
        if firstFrame is None:
            print('Frame not created', file=sys.stderr)
            sys.exit(err.unknown_frame)
        else:
            # Check if variable exists
            if first_var not in firstFrame:
                print('Writing to non-existing variable', file=sys.stderr)
                sys.exit(err.unknown_var)
            else:
                if instr[3] == 'var':
                    # You can move variable into variable
                    second_frame, second_var = self.split_var(instr[4])
                    secondFrame = self.getFrame(second_frame)
                    # Check if frame exists
                    if secondFrame is None:
                        print('Frame not created', file=sys.stderr)
                        sys.exit(err.unknown_frame)
                    else:
                        # Check if variable exists
                        if second_var not in secondFrame:
                            print('Writing to non-existing variable', file=sys.stderr)
                            sys.exit(err.unknown_var)
                        else:
                            if secondFrame[second_var]['type'] is None and secondFrame[second_var]['data'] is None:
                                print('Writing empty to empty', file=sys.stderr)
                                sys.exit(err.unknown_value)
                            else:
                                firstFrame[first_var]['type'] = secondFrame[second_var]['type']
                                firstFrame[first_var]['data'] = secondFrame[second_var]['data']
                else:
                    firstFrame[first_var]['data'] = instr[4]
                    firstFrame[first_var]['type'] = instr[3]

    def _pushs(self, instr, where):
        new = []
        data, type = self.varargs(instr)
        new.append(type)
        new.append(data)
        self.data_stack.insert(0, new)

    def _pops(self, instr, where):
        if not self.data_stack:
            print('Popping nothing from data stack', file=sys.stderr)
            sys.exit(err.unknown_value)
        else:
            new = self.data_stack.pop(0)
            instr.append(new[0])
            instr.append(new[1])

        self._move(instr, where)

    ## Every instruction that changes variable value has:
    # tmp_type = instr[3]
    # tmp_data = instr[4]
    #
    # ....
    #
    # self._move(instr, where)
    # instr[3] = tmp_type
    # instr[4] = tmp_data
    ## Because I'm storing result of instruction to instr[3], instr[4]
    ## and in case there's a jump back it stays changed

    def _numeric(self, instr, where):
        tmp_type = instr[3]
        tmp_data = instr[4]
        data1, type1, data2, type2 = self.triargs(instr)


        # Type checks
        if type1 != 'int' or type2 != 'int':
            print('Wrong type in add', file=sys.stderr)
            sys.exit(err.type)

        instr[3] = 'int'

        if instr[0] == 'ADD':
            instr[4] = data1 + data2
        elif instr[0] == 'SUB':
            instr[4] = data1 - data2
        elif instr[0] == 'MUL':
            instr[4] = data1 * data2
        elif instr[0] == 'IDIV':
            if data2 == 0:
                print('Div by zero', file=sys.stderr)
                sys.exit(err.wrong_value)
            else:
                instr[4] = data1 // data2
        
        self._move(instr, where)
        instr[3] = tmp_type
        instr[4] = tmp_data

    def _EQ(self, instr, where):
        tmp_type = instr[3]
        tmp_data = instr[4]
        data1, type1, data2, type2 = self.triargs(instr)

        # Type checks
        if type1 != type2:
            if type1 != 'nil' and type2 != 'nil':
                print('Wrong type in', instr[0], file=sys.stderr)
                sys.exit(err.type)

        instr[3] = 'bool'

        if data1 == data2:
            instr[4] = 'true'
        else:
            instr[4] = 'false'
        
        self._move(instr, where)
        instr[3] = tmp_type
        instr[4] = tmp_data


    def _LT(self, instr, where):
        tmp_type = instr[3]
        tmp_data = instr[4]
        data1, type1, data2, type2 = self.triargs(instr)


        # Type checks
        if type1 != type2 or type1 == 'nil' or type2 == 'nil':
            print('Wrong type in', instr[0], file=sys.stderr)
            sys.exit(err.type)

        instr[3] = 'bool'

        if data1 < data2:
            instr[4] = 'true'
        else:
            instr[4] = 'false'
        self._move(instr, where)
        instr[3] = tmp_type
        instr[4] = tmp_data


    def _GT(self, instr, where):
        tmp_type = instr[3]
        tmp_data = instr[4]
        data1, type1, data2, type2 = self.triargs(instr)

        # Type checks
        if type1 != type2 or type1 == 'nil' or type2 == 'nil':
            print('Wrong type in', instr[0], file=sys.stderr)
            sys.exit(err.type)

        instr[3] = 'bool'

        if data1 > data2:
            instr[4] = 'true'
        else:
            instr[4] = 'false'
        self._move(instr, where)
        instr[3] = tmp_type
        instr[4] = tmp_data


    def _logic(self, instr, where):
        tmp_type = instr[3]
        tmp_data = instr[4]
        data1, type1, data2, type2 = self.triargs(instr)

        # Type checks
        if type1 != 'bool' or type2 != 'bool':
            print('Wrong types in and', file=sys.stderr)
            sys.exit(err.type)

        instr[3] = 'bool'

        if data1 != 'true':
            data1 = False
        else:
            data1 = True
        if data2 != 'true':
            data2 = False
        else:
            data2 = True

        if instr[0] == 'AND':
            instr[4] = data1 and data2
        else:
            instr[4] = data1 or data2

        if instr[4]:
            instr[4] = 'true'
        else:
            instr[4] = 'false'

        self._move(instr, where)
        instr[3] = tmp_type
        instr[4] = tmp_data

    def _not(self, instr, where):
        tmp_type = instr[3]
        tmp_data = instr[4]
        data1, type1 = self.dualargs(instr)

        # Type checks
        if type1 != 'bool':
            print('Wrong types in and', file=sys.stderr)
            sys.exit(err.type)

        instr[3] = 'bool'

        if data1 != 'true':
            data1 = False
        else:
            data1 = True

        instr[4] = not data1

        if instr[4]:
            instr[4] = 'true'
        else:
            instr[4] = 'false'

        self._move(instr, where)
        instr[3] = tmp_type
        instr[4] = tmp_data

    def _int2char(self, instr, where):
        tmp_type = instr[3]
        tmp_data = instr[4]
        data, type = self.dualargs(instr)

        # Type checks
        if type != 'int':
            print('Wrong types in int2char', file=sys.stderr)
            sys.exit(err.type)
        
        instr[3] = 'str'
        try:
            instr[4] = chr(data)
        except:
            print('Wrong types in int2char', file=sys.stderr)
            sys.exit(err.wrong_string)

        self._move(instr, where)
        instr[3] = tmp_type
        instr[4] = tmp_data

    def _stri2int(self, instr, where):
        tmp_type = instr[3]
        tmp_data = instr[4]
        data1, type1, data2, type2 = self.triargs(instr)

        # Type checks
        if type1 != 'str' or type2 != 'int':
            print('Wrong types in stri2int', file=sys.stderr)
            sys.exit(err.type)

        if data2 >= len(data1)-1 or data2 < 0:
            print('Wrong types in stri2int', file=sys.stderr)
            sys.exit(err.wrong_string)

        instr[3] = 'int'
        instr[4] = ord(data1[data2])

        self._move(instr, where)
        instr[3] = tmp_type
        instr[4] = tmp_data

    def _read(self, instr, where):
        tmp_type = instr[3]
        tmp_data = instr[4]
        tmp = ''

        # Input file was not given
        if self.input == 'false':
            tmp = input()
        else:
            tmp = self.input.readline()

        instr[3] = instr[4]

        # Type checks
        if instr[3] != 'string':
            tmp = tmp.strip()

        if instr[3] == 'bool':
            if tmp == '':
                tmp = 'nil'
                instr[3] = 'nil'
            elif tmp.lower() != 'true':
                tmp = 'false'
            else:
                tmp = tmp.lower()
        elif instr[3] == 'int':
            if tmp == '':
                instr[3] = 'nil'
                tmp = 'nil'
            if not tmp.isnumeric():
                tmp = tmp.split('-', 1)
                if tmp[0] == '' and tmp[1].isnumeric():
                    tmp = int(tmp[1]) * -1
                else:
                    instr[3] = 'nil'
                    tmp = 'nil'
            else:
                tmp = int(tmp)
        elif instr[3] == 'string':
            instr[3] = 'str'
            if tmp == '':
                tmp = 'nil'
                instr[3] = 'nil'
            else:
                tmp = tmp.strip()
                
        instr[4] = tmp

        self._move(instr, where)
        instr[3] = tmp_type
        instr[4] = tmp_data


    def _write(self, instr, where):
        nil = False

        # Type checks
        if instr[1] == 'var':
            data, type = self.getValues(instr[2], None, None)
            if type == 'nil':
                nil = True
        else:
            data = instr[2]
            if instr[1] == 'nil':
                nil = True

        if nil:
            print('', end='')
        else:
            print(data, end ='')

    def _concat(self, instr, where):
        tmp_type = instr[3]
        tmp_data = instr[4]
        data1, type1, data2, type2 = self.triargs(instr)

        # Type checks
        if type1 != 'str' or type2 != 'str':
            print('Wrong type in concat', file=sys.stderr)
            sys.exit(err.type)

        instr[3] = 'str'
        instr[4] = data1 + data2

        self._move(instr, where)
        instr[3] = tmp_type
        instr[4] = tmp_data
    
    def _strlen(self, instr, where):
        tmp_type = instr[3]
        tmp_data = instr[4]
        data1, type1 = self.dualargs(instr)

        # Type checks
        if type1 != 'str':
            print('Wrong type in strlen', file=sys.stderr)
            sys.exit(err.type)

        instr[3] = 'int'
        instr[4] = len(data1)

        self._move(instr, where)
        instr[3] = tmp_type
        instr[4] = tmp_data
    
    def _getchar(self, instr, where):
        tmp_type = instr[3]
        tmp_data = instr[4]
        data1, type1, data2, type2 = self.triargs(instr)

        # Type checks
        if type1 != 'str' or type2 != 'int':
            print('Wrong type in getchar', file=sys.stderr)
            sys.exit(err.type)

        if data2 > len(data1)-1 or data2 < 0:
            print('Getting char out of array', file=sys.stderr)
            sys.exit(err.wrong_string)

        instr[3] = 'str'
        instr[4] = data1[data2]

        self._move(instr, where)
        instr[3] = tmp_type
        instr[4] = tmp_data
    
    def _setchar(self, instr, where):
        tmp_type = instr[3]
        tmp_data = instr[4]
        data1, type1, data2, type2 = self.triargs(instr)
        vardata, vartype = self.varargs(instr)

        # Type checks
        if type1 != 'int' or type2 != 'str' or vartype != 'str':
            print('Wrong type in setchar', file=sys.stderr)
            sys.exit(err.type)

        if len(data2) < 1 or data1 > len(vardata)-1 or data1 < 0:
            print('Setting char out of array', file=sys.stderr)
            sys.exit(err.wrong_string)

        instr[4] = vardata[data1+1:]
        instr[3] = vardata[:data1]

        instr[4] = instr[3] + data2[0] + instr[4]
        instr[3] = 'str'

        self._move(instr, where)
        instr[3] = tmp_type
        instr[4] = tmp_data
    
    # Fills first var with type of second symbol
    def _type(self, instr, where):
        first_frame, first_var = self.split_var(instr[2])
        firstFrame= self.getFrame(first_frame)
        if firstFrame is None:
            print('firstFrame not created', file=sys.stderr)
            sys.exit(err.unknown_frame)
        else:
            if first_var not in firstFrame:
                print('Writing to non-existing promenna', file=sys.stderr)
                sys.exit(err.unknown_var)
            else:
                if instr[3] == 'var':
                    # It may need to check variable type
                    second_frame, second_var = self.split_var(instr[4])
                    secondFrame = self.getFrame(second_frame)
                    if secondFrame is None:
                        print('Frame not created', file=sys.stderr)
                        sys.exit(err.unknown_frame) 
                    else:
                        if second_var not in secondFrame:
                            print('Frame not created', file=sys.stderr)
                            sys.exit(err.unknown_var)
                        else:
                            # Fill first_variable according to second_variables type
                            if secondFrame[second_var]['type'] == 'int':
                                firstFrame[first_var]['data'] = 'int'
                            elif secondFrame[second_var]['type'] == 'str':
                                firstFrame[first_var]['data'] = 'string'
                            elif secondFrame[second_var]['type'] == 'bool':
                                firstFrame[first_var]['data'] = 'bool'
                            elif secondFrame[second_var]['type'] == 'nil':
                                firstFrame[first_var]['data'] = 'nil'
                            else:
                                firstFrame[first_var]['data'] = ''
                            firstFrame[first_var]['type'] = 'str'
                else:
                    # Fill first_variable according to second_variables type
                    if instr[3] == 'int':
                        firstFrame[first_var]['data'] = 'int'
                    elif instr[3] == 'str':
                        firstFrame[first_var]['data'] = 'string'
                    elif instr[3] == 'bool':
                        firstFrame[first_var]['data'] = 'bool'
                    elif instr[3] == 'nil':
                        firstFrame[first_var]['data'] = 'nil'
                    firstFrame[first_var]['type'] = 'str'
    
    # Skip, all labels were taken care of before
    def _label(self, instr, where):
        pass

    # Method to support all kinds of jumps
    def _jumps(self, instr, where):
        for label in self.labels:
            if label == instr[2]:
                self.position = self.labels.get(label)
        if self.position == -1:
            print('Unknown label', instr[2], file=sys.stderr)
            sys.exit(err.semantic)

        if instr[0] == 'CALL':
            self.position_stack.insert(0, where)
            return

        if instr[0] == 'JUMP':
            return

        data1, type1, data2, type2 = self.triargs(instr)

        if type1 != type2:
            if type1 != 'nil' and type2 != 'nil':
                print('Wrong type in', instr[0], file=sys.stderr)
                sys.exit(err.type)

        # self.position -1 means not jumping
        if instr[0] == 'JUMPIFEQ':
            if data1 != data2:
                self.position = -1
        if instr[0] == 'JUMPIFNEQ':
            if data1 == data2:
                self.position = -1

    # Gets value to return to from position_stack
    def _return(self, instr, where):
        if not self.position_stack:
            print('Nowhere to return to', file=sys.stderr)
            sys.exit(err.unknown_value)
        else:
            self.position = self.position_stack.pop(0)
    
    # Exits program with exit number saved in var
    def _exit(self, instr, where):
        data, type = self.varargs(instr)
        if type != 'int':
            print('Wrong type in', instr[0], file=sys.stderr)
            sys.exit(err.type)

        if data < 0 or data > 49:
            print('Wrong number in', instr[0], data, file=sys.stderr)
            sys.exit(err.wrong_value)

        sys.exit(data)
    

    # Can't write to stdin, only stderr
    # won't be tested so not implemented
    def _dprint(self, instr, where):
        pass
    
    def _break(self, instr, where):
        pass