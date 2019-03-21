import ply.yacc as yacc

# Variables are not intialized, and can not be used until value is assigned to
# them, otherwise it is considered an error.


# TODO: better array cells handling
# TODO: using loop iterator as value is currently not possible


import tokenizer
import language
import sys


# Global exception handling.
# Because we can.
def my_except_hook(exctype, value, traceback):
    if exctype in language.ERRORS:
        print(value)
        return value.return_code

    else:
        sys.__excepthook__(exctype, value, traceback)


sys.excepthook = my_except_hook


SET_DEBUG = False


program = language.Program()


class IdentifierRedefinitionError(language.LanguageException):
    """Raise when identifier is redeclared."""
    pass


class NoSuchIdentifierError(language.LanguageException):
    """Raise when there is no identifier remembered with such name."""
    pass

class NameAlreadyTakenError(language.LanguageException):
    """Raise when user tries to create local variable with ambiguous name."""
    pass


class IdentifiersManager:
    # Array cells are treated as array substuff, so are not managed here.
    # Only variables and arrays have a meaning here.

    def __init__(self):
        self.arrays = {}
        self.variables = {}
        self.local_variables = {}
        self.numbers = {}

    def add_identifier(self, identifier: language.Identifier):
        name = identifier.name
        if name in self.arrays or name in self.variables:
            raise IdentifierRedefinitionError("Redefinition of a variable.", 32)

        if isinstance(identifier, language.Variable):
            self.variables[name] = identifier
        elif isinstance(identifier, language.Array):
            self.arrays[name] = identifier
        else:
            print("SUCH IDENTIFIER TYPE NOT SUPPORTED")
            sys.exit(-1)

    def identifier_exists(self, identifier_name):
        if identifier_name in self.arrays or identifier_name in self.variables:
            return True

        return False

    def get_identifier(self, identifier_name):
        if identifier_name in self.arrays:
            return self.arrays[identifier_name]
        if identifier_name in self.variables:
            return self.variables[identifier_name]

        if identifier_name in self.local_variables:
            return self.local_variables[identifier_name]

        raise NoSuchIdentifierError("No Such identifier known.", 30)

    def get_variable(self, identifier_name):
        if identifier_name in self.local_variables:
            return self.local_variables[identifier_name]

        if identifier_name in self.variables:
            return self.variables[identifier_name]

        raise NoSuchIdentifierError("No variable with such id(" +
                                    identifier_name + ")", 30)

    def add_local_variable(self, identifier_name):
        if identifier_name in self.variables or identifier_name in self.arrays:
            raise NameAlreadyTakenError("Variable or array with that name\
                                        already exists", 32)
        self.local_variables[identifier_name] = language.TempIdentifier(identifier_name)

    def get_local_variable(self, identifier_name):
        if identifier_name in self.local_variables:
            return self.local_variables[identifier_name]
        else:
            raise NoSuchIdentifierError("No local variable with such id.", 33)

    def del_local_variable(self, identifier_name):
        del self.local_variables[identifier_name] 

    def get_array(self, identifier_name):
        if identifier_name in self.arrays:
            return self.arrays[identifier_name]

        raise NoSuchIdentifierError("No array with such id.", 30)


# Identifiers replace variables and arrays and numbers.
IDENTIFIERS_MANAGER = IdentifiersManager()


def print_error(p, string, return_code=1):
    """Print error message and return non-zero exit code."""
    print(string)
    print("On line: " + str(p.lexer.lineno))
    sys.exit(return_code)


def debug_print(p):
    global SET_DEBUG 
    if SET_DEBUG:
        for val in p:
            if val is not None:
                print(val)


tokens = tokenizer.tokens

def p_program(p):
    'program            : DECLARE declarations IN commands END'
    program.set_block(p[4])


def p_declarations(p):
    '''declarations     : declarations variable_dec
                        | declarations array_dec
                        | '''
    pass 


def p_variable_dec(p):
    'variable_dec           : pidentifier SEMICOLON'
    if IDENTIFIERS_MANAGER.identifier_exists(p[1]):
        print_error(p, "Redefinition of identifier " + p[1])

    IDENTIFIERS_MANAGER.add_identifier(language.Variable(p[1]))


def p_array_dec(p):
    'array_dec              : pidentifier LPAREN NUMBER COLON NUMBER RPAREN SEMICOLON'
    if IDENTIFIERS_MANAGER.identifier_exists(p[1]):
        print_error(p, "Redefinition of identifier " + p[1])
    try:
        IDENTIFIERS_MANAGER.add_identifier(language.Array(p[1], int(p[3]),
                                                          int(p[5])))
    except language.LanguageException as e:
        print_error(p, e.args[0], e.return_code)


def p_commands(p):
    '''commands         : multi_commands
                        | single_command'''
    p[0] = p[1]


def p_multi_commands(p):
    '''multi_commands   : commands single_command'''
    p[0] = p[1] + p[2]



def p_single_command(p):
    '''single_command   : single_command_simple
                        | single_command_block'''
    temp = language.Commands()
    p[0] = temp + p[1]


def p_single_command_simple(p):
    '''single_command_simple    : assign
                                | write
                                | read'''
    p[0] = p[1]


def p_single_command_block(p):
    '''single_command_block   : advanced_if
                                | simple_if
                                | while
                                | do_while
                                | for
                                | for_backwards'''
    p[0] = p[1]


def p_simple_if(p):
    '''simple_if        : IF condition THEN commands ENDIF'''
    p[0] = language.If(p[2], p[4])


def p_advanced_if(p):
    '''advanced_if      : IF condition THEN commands ELSE commands ENDIF'''
    p[0] = language.IfElse(p[2], p[4], p[6])


def p_while(p):
    '''while            : WHILE condition DO commands ENDWHILE'''
    p[0] = language.While(p[2], p[4])


def p_for(p):
    '''for              : FOR pidentifier for_identifier FROM value TO value DO commands ENDFOR'''
    if IDENTIFIERS_MANAGER.identifier_exists(p[2]):
        print_error(p, "Loop identifier has same name as variable.", 28)
    try:
        p[0] = language.For(IDENTIFIERS_MANAGER.get_local_variable(p[2]), p[5], p[7], p[9])
    except language.ForLoopIdentifierError as e:
        print_error(p, e.args[0], e.return_code)
    except language.LoopIteratorModified as e:
        print_error(p, e.args[0], e.return_code)
    except language.NotCorrectIteratorUse as e:
        print_error(p, e.args[0], e.return_code)
    except language.VariableNotInitializedError as e:
        print_error(p, e.args[0], e.return_code)


    # Assign loop object to iterator.
    IDENTIFIERS_MANAGER.get_local_variable(p[2]).loop = p[0]

    IDENTIFIERS_MANAGER.del_local_variable(p[2])


def p_for_backwards(p):
    '''for_backwards    : FOR pidentifier for_identifier FROM value DOWNTO value DO commands ENDFOR'''
    if IDENTIFIERS_MANAGER.identifier_exists(p[2]):
        print_error(p, "Loop identifier has same name as variable.", 28)

    try:
        p[0] = language.ForBackwards(IDENTIFIERS_MANAGER.get_local_variable(p[2]), p[5], p[7], p[9])
    except language.ForLoopIdentifierError as e:
        print_error(p, e.args[0], e.return_code)
    except language.LoopIteratorModified as e:
        print_error(p, e.args[0], e.return_code)
    except language.NotCorrectIteratorUse as e:
        print_error(p, e.args[0], e.return_code)
    except language.VariableNotInitializedError as e:
        print_error(p, e.args[0], e.return_code)


    # Assign loop object to iterator.
    IDENTIFIERS_MANAGER.get_local_variable(p[2]).loop = p[0]

    IDENTIFIERS_MANAGER.del_local_variable(p[2])


def p_for_identifier(p):
    '''for_identifier :'''

    if p[-1] in IDENTIFIERS_MANAGER.local_variables:
        print_error(p, "Loop iterator has same name as super loop iterator", 36)

    IDENTIFIERS_MANAGER.add_local_variable(p[-1])

def p_do_while(p):
    '''do_while         : DO commands WHILE condition ENDDO'''
    p[0] = language.DoWhile(p[4], p[2])


def p_read(p):
    '''read             : READ identifier SEMICOLON'''
    try:
        if isinstance(p[2], language.ArrayCell):
            p[0] = language.Read(p[2])
        else:
            p[0] = language.Read(IDENTIFIERS_MANAGER.get_identifier(p[2].name))
    except NoSuchIdentifierError as e:
        print_error(p, e.args[0], e.return_code)


def p_write(p):
    '''write            : WRITE value SEMICOLON'''
    try:
        p[0] = language.Print(p[2])
    except language.VariableNotInitializedError as e:
        print_error(p, e.args[0], e.return_code)


def p_assign(p):
    'assign             : identifier ASSIGN expression SEMICOLON'
    if isinstance(p[1], language.Variable):
        try:
            # We can't just get variable name here, identifier can be an array.
            temp = IDENTIFIERS_MANAGER.get_variable(p[1].name)
            #if IDENTIFIERS_MANAGER.identifier_exists(p[1].name):
            p[0] = language.Assign(temp, p[3])
        except NoSuchIdentifierError as e:
            print_error(p, e.args[0], e.return_code)
        except language.LoopIteratorModified as e:
            print_error(p, e.args[0], e.return_code)
    elif isinstance(p[1], language.ArrayCell):
        # Try to set [0] as an array cell.
        p[0] = language.Assign(p[1], p[3])
    elif isinstance(p[1], language.TempIdentifier):
        print_error(p, "Loop iterator modified inside loop.", 38)



def p_expression(p):
    '''expression       : single_expression
                        | expression_operation'''
    p[0] = p[1]


def p_single_expression(p):
    '''single_expression : value'''
    try:
        p[0] = language.ExpressionSingle(p[1])
    except language.VariableNotInitializedError as e:
        print_error(p, e.args[0], e.return_code)
    except language.ArrayInExpressionError as e:
        print_error(p, e.args[0], e.return_code)


def p_expression_operation(p):
    '''expression_operation : value PLUS value
                        | value MINUS value
                        | value MULTIPLY value
                        | value DIVIDE value
                        | value MODULO value'''
    try:
        p[0] = language.ExpressionOperation(p[1], p[2], p[3])
    except language.VariableNotInitializedError as e:
        print_error(p, e.args[0], e.return_code)
    except language.ArrayInExpressionError as e:
        print_error(p, e.args[0], e.return_code)


def p_condition(p):
    '''condition        : value EQUALS value
                        | value NOT_EQUALS value
                        | value LOWER_THEN value
                        | value GREATER_THEN value
                        | value LOWER_EQUAL value
                        | value GREATER_EQUAL value'''
    # TODO: should i keep track of all conditions that happen throughout the
    # code?
    try:
        p[0] = language.Condition(p[1], str(p[2]), p[3])
    except language.VariableNotInitializedError as e:
        print_error(p, e.args[0], e.return_code)


def p_value(p):
    '''value            : number
                        | identifier'''
    p[0] = p[1]


def p_number(p):
    '''number           : NUMBER'''
    if p[1] in IDENTIFIERS_MANAGER.numbers:
        p[0] = IDENTIFIERS_MANAGER.numbers[p[1]]
    else:
        p[0] = language.Number(int(p[1]))
        IDENTIFIERS_MANAGER.numbers[p[1]] = p[0]


def p_identifier(p):
    '''identifier       : variable
                        | array_cell'''
    p[0] = p[1]


def p_variable(p):
    '''variable         : pidentifier'''
    try:
        p[0] = IDENTIFIERS_MANAGER.get_variable(p[1])
    except NoSuchIdentifierError as e:
        print_error(p, e.args[0], e.return_code)


def p_array_cell(p):
    '''array_cell       : array_variable
                        | array_NUMBER'''
    p[0] = p[1]


def p_array_variable(p):
    '''array_variable   : pidentifier LPAREN pidentifier RPAREN'''
    try:
        array = IDENTIFIERS_MANAGER.get_array(p[1])
        variable = IDENTIFIERS_MANAGER.get_variable(p[3])
    except NoSuchIdentifierError as e:
        print_error(p, e.args[0], e.return_code)
    # TODO: We can't be sure whether value exists or not, when we use variable
    # to define array index.
    p[0] = language.ArrayCellVariable(array, variable)
    p[0].set_value_as_known()
    array.add_cell(p[0])


def p_array_NUMBER(p):
    '''array_NUMBER   : pidentifier LPAREN NUMBER RPAREN'''
    if p[3] in IDENTIFIERS_MANAGER.numbers:
        number = IDENTIFIERS_MANAGER.numbers[p[3]]
    else:
        number = language.Number(int(p[3]))
    try:
        array = IDENTIFIERS_MANAGER.get_array(p[1])
    except NoSuchIdentifierError as e:
        print_error(p, e.args[0], e.return_code)

    if number.value > array.stop_index or number.value < array.start_index:
        print_error(p, "Array cell index out of array bounds.", 26)
    # TODO: One more time, we can't be sure. Maybe it was intialized previously
    # with an variable based index.
    if number.value in array.cells:
        p[0] = array.cells[number.value]
    else:
        p[0] = language.ArrayCellNumber(array, number)
        p[0].set_value_as_known()
        array.add_cell(p[0])


def p_error(p):
    print_error(p, "Syntax error: " + p.value, 2)


def get_code(filename):
    lexer = tokenizer.get_lexer()
    parser = yacc.yacc()

    with open(filename, 'r') as codefile:
        content = codefile.read()
    parser.parse(content, lexer=lexer)

    return program


def get_code_from_string(string):
    lexer = tokenizer.get_lexer()
    parser = yacc.yacc()

    parser.parse(string, lexer=lexer)

    return program


def reset():
    """Used for resetting globals when testing."""
    global program
    global IDENTIFIERS_MANAGER
    program = language.Program()
    IDENTIFIERS_MANAGER.numbers = {}
    IDENTIFIERS_MANAGER = IdentifiersManager()


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: parser.py file_name")
        sys.exit(1)

    program = get_code(sys.argv[1])
    #program.finish_parsing()
    program.print_out()
