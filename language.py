"""Classes describing basic blocks of code in language."""

from abc import ABC, abstractmethod, abstractproperty


class LanguageException(Exception):
    """Base exception for this module."""
    def __init__(self, message_string: str, return_code: int):
        super().__init__(message_string)
        self.return_code = return_code


class ArrayNegativeLengthError(LanguageException):
    """Raise when array length is smaller than 0."""
    pass


class ArrayIncorrectBoundError(LanguageException):
    """Raise when one of arrays bounds is smaller than 0."""
    pass


class VariableNotInitializedError(LanguageException):
    """Raise when one of arrays bounds is smaller than 0."""
    pass


class ValueComparedWithArrayError(LanguageException):
    """Raise when array is compared with variable in Condition."""
    pass


class ArrayInExpressionError(LanguageException):
    """Raise when array is used in expression (not it's cell)."""
    pass


class ForLoopIdentifierError(LanguageException):
    """Raise when loop iterator is redeclared in one of subloops."""
    pass


class LoopIteratorModified(LanguageException):
    """Raise when loop iterator value is changed in loop."""
    pass


class NotCorrectIteratorUse(LanguageException):
    """Raised when iterator is used as start or stop value."""
    pass


ERRORS = (ArrayNegativeLengthError, ArrayIncorrectBoundError,
          VariableNotInitializedError)


def traverse(block, result: list):
    for item in block.iterate():
        try:
            iterator = iter(item)
            traverse_rec(iterator, result)
        except TypeError:
            result.append(item)


def traverse_rec(iterator, result: list):
    for item in iterator:
        try:
            iterator = iter(item)
            traverse_rec(iterator, result)
        except TypeError:
            result.append(item)


class Commands:
    """Describe set of command (code block)."""
    def __init__(self):
        self.commands = []

    def add_command(self, command) -> None:
        """Add single command object to block."""
        self.commands.append(command)

    def add_command_at_the_beggining(self, command) -> None:
        """Add single command object to start of the block."""
        temp = Commands()
        temp.add_command(command)
        self.commands = temp.commands + self.commands

    def add_command_at_position(self, command, position: int) -> None:
        """Add single command object at specified index."""
        temp = self.commands[:position] + [command] + self.commands[position:]
        self.commands = temp

    def add_block(self, block) -> None:
        """Add command block to block."""
        self.commands += block.commands

    def get_all(self) -> list:
        """Return list of all commands."""
        return self.commands

    def print_out(self, indentation=0):
        """Print info about every command or block (debug)."""
        print(" " * indentation + "--> BLOCK START")
        for something in self.commands:
            something.print_out(indentation + 4)
        print(" " * indentation + "--> BLOCK END")

    def get_all_containing(self, item):
        """Return all subcommands/commands containing specified item."""
        temp = []
        for command in self.commands:
            temp += command.get_all_containing(item)

        return temp

    def get_all_instances(self, item):
        """Return all subcommands/commands that are type of specified item."""
        temp = []
        if isinstance(self, item):
            temp.append(self)
        for command in self.commands:
            temp += command.get_all_instances(item)

        return temp

    def get_path_to(self, item):
        for command in self.commands:
            if command.get_path_to(item):
                return [self] + command.get_path_to(item)
        return False

    def remove(self, item):
        if item in self.commands:
            self.commands.remove(item)
        else:
            for command in self.commands:
                command.remove(item)

    def contains(self, item):
        if len(self.get_all_containing(item)) > 0:
            return True
        return False

    def iterate(self):
        for command in self.commands:
            yield command.iterate()
        return self

    def __add__(self, value):
        to_return = Commands()
        if isinstance(value, Commands):
            to_return.commands = self.commands
            to_return.add_block(value)
        elif isinstance(value, Command):
            to_return.commands = self.commands
            to_return.add_command(value)
        else:
            raise Exception("No such value can be added!")

        return to_return

    def __iter__(self):
        return iter(self.commands)

    def __len__(self):
        return len(self.commands)

    def is_in(self, item):
        """True if command is subcommand of class at one point."""
        if type(self) == item:
            return True
        try:
            return self.parent.is_in(item)
        except AttributeError:
            return False

    def get_ordered_list(self):
        """Return all commands as ordered list (tree traverse pre)."""
        result = []
        traverse(self, result)
        return result


class Command(ABC):
    """Describe single one command (master interface)."""

    def print_out(self, indentation=0):
        """Display debug info about command."""
        #print("--COMMAND")
        print(" " * indentation + str(self))
        #print("--COMMAND END")

    def get_all_instances(self, item):
        """Return all subcommands/commands that are type of specified item."""
        temp = []
        if isinstance(self, item):
            temp.append(self)

        return temp


    def remove(self, item):
        pass

    def contains(self, item):
        if len(self.get_all_containing(item)) > 0:
            return True
        return False

    def is_in(self, item):
        """True if command is subcommand of class at one point."""
        if type(self) == item:
            return True
        return self.parent.is_in(item)

    def get_path_to(self, item):
        if self is item:
            return [self]
        return False

    def iterate(self):
        return self

    def __add__(self, value):
        """Adding command to command creates a command block."""
        to_return = Commands()
        to_return.add_command(self)
        to_return.add_command(value)
        return to_return

class Program:
    """Program is master abstraction over program, it consists of blocks of
    code, and should show dependencies between blocks."""
    # TODO: DAG , tree, whatever

    def __init__(self):
        self.declarations = []
        self.block = Commands()

    def set_block(self, block: Commands):
        """Make current path a block, and add new one."""
    #    self.blocks.append(self.curr_block)
    #    self.curr_block = Commands()
        self.block = block

    def print_out(self):
        self.block.print_out()



#TODO: describe commands.



class Value(ABC):
    """Master class for value."""

    #@property
    def value(self):
        return self.value

    #@value.setter
    #def value(self, value):
    #    self.value = value

    @abstractmethod
    def __str__(self):
        return str(self.value)

    def contains(self, item):
        return self is item

    def get_path_to(self, item):
        if self is item:
            return [self]
        return False

    def get_all_instances(self, item):
        """Return all subcommands/commands that are type of specified item."""
        temp = []
        if isinstance(self, item):
            temp.append(self)

        return temp

    def can_be_used(self):
        """Raise exception if value can't be used in numeric context."""
        if not self.value_is_known:
            message = "Variable has not been initialized yet."
            raise VariableNotInitializedError(message, 22)

    def set_value_as_known(self):
        self.value_is_known = True

    def set_value_as_unknown(self):
        self.value_is_known = False


class Number(Value):
    """Describe number that is known at compile-time."""
    def __init__(self, value: int):
        self.value = value
        self.value_is_known = True

    def __str__(self):
        return "num(" + str(self.value) + ")"

    def can_be_used(self):
        """Number is ready to use by definition, empty method."""
        pass

    def __eq__(self, item):
        if self.value == item.value:
            return True
        else:
            return False

    def __hash__(self):
        return id(self)


class Identifier(Value):
    """Master class for identifier."""
    value_is_known = False
    memory_cell = "N/A"

    name = "DEFAULT ID NAME"

    def contains(self, item):
        return self is item


class VariableBase(Identifier):
    """Master class for variable-like stuff."""
    # Some stuff for optimalisation.


class TempIdentifier(VariableBase):
    """Class for loop iterator."""
    value_is_known = True

    def __init__(self, name: str):
        self.name = name
        self.value_is_known = True

    def __str__(self):
        return ("loop_iterator(" + self.name + ")[" + str(self.memory_cell) +
                "](ID=" + str(id(self)) + ")")


class Variable(VariableBase):
    """Describe single variable."""
    def __init__(self, name: str):
        """Name is variable name in that case."""
        self.register = False
        self.name = name
        self.value_is_known = False
        self.dynamically_allocated = False

    def __str__(self):
        return ("var(" + self.name + ")[" + str(self.memory_cell) + "](" +
                str(self.register) + ")(" + str(self.dynamically_allocated) +
                ")")

    def contains(self, item):
        return self is item


class Array(Identifier):
    """Describe an array."""
    def __init__(self, name: str, start_index: int, stop_index: int):
        if start_index < 0 or stop_index < 0:
            message = "One of array bounds values is smaller than 0"
            raise ArrayIncorrectBoundError(message, 21)
        self.length = stop_index - start_index + 1
        if self.length <= 0:
            message = "Array has negative length"
            raise ArrayNegativeLengthError(message, 22)

        self.start_index = start_index
        self.stop_index = stop_index
        self.name = name
        self.cells = {}

    def value(self):
        return self.name

    def __str__(self):
        return ("array(" + self.name + ")" + "[" + str(self.start_index) +
                ":" + str(self.stop_index) + "]")

    def add_cell(self, cell):
        self.cells[cell.index_val] = cell


class ArrayCell(Identifier):
    """Master class for array cells."""
    array: Array = None
    index: Variable = None
    index_val: str = None
    value_is_known: bool = False
    name: str = None


class ArrayCellVariable(ArrayCell):
    """Describe array cell, indexed by variable."""
    def __init__(self, array: Array, variable: Variable):
        self.array = array
        self.index = variable
        self.index_val = variable.name
        self.value_is_known = False
        self.name = array.name
        self.dynamically_allocated = False

    def __str__(self):
        return ("array_cell(" + self.array.name + ")[" + str(self.index)
                + "]")

    def contains(self, item):
        if self.array is item or self.index is item:
            return True
        return False


class ArrayCellNumber(ArrayCell):
    """Describe array cell, indexed by number."""
    def __init__(self, array: Array, number: Number):
        self.array = array
        self.index = number
        self.index_val = number.value
        self.value_is_known = False
        self.name = array.name
        self.dynamically_allocated = False

    def contains(self, item):
        if self.array is item or self.index is item:
            return True
        return False

    def __str__(self):
        return ("array_cell(" + self.array.name + ")[" + str(self.index)
                + "]")


class Expression:
    """Describe single expression (master interface)."""
    pass


class ExpressionSingle(Expression):
    def __init__(self, value: Value):
        value.can_be_used()
        self.value = value
        self.check()

    def __str__(self):
        return "single_expression(" + str(self.value) + ")"

    def contains(self, item):
        if self.value.contains(item):
            return True
        return False

    def get_path_to(self, item):
        if self is item:
            return [self]
        elif self.value.get_path_to(item):
            return [self] + self.value.get_path_to(item)
        return False

    def get_all_instances(self, item):
        """Return all subcommands/commands that are type of specified item."""
        temp = []
        if isinstance(self, item):
            temp.append(self)
        temp += self.value.get_all_instances(item)

        return temp


    def check(self):
        if isinstance(self.value, Array):
            raise ArrayInExpressionError("Array used in expression.", 31)


class ExpressionOperation(Expression):
    def __init__(self, first: Value, operator: str, second: Value):
        first.can_be_used()
        second.can_be_used()
        self.first = first
        self.operator = operator
        self.second = second
        self.check()

    def contains(self, item):
        if self.first.contains(item) or self.second.contains(item):
            return True
        return False

    def get_path_to(self, item):
        if self is item:
            return [self]
        elif self.first.get_path_to(item):
            return [self] + self.first.get_path_to(item)
        elif self.second.get_path_to(item):
            return [self] + self.second.get_path_to(item)
        return False

    def __str__(self):
        return ("operation_expression(" + str(self.first) + self.operator +
                str(self.second) + ")")

    def check(self):
        if isinstance(self.first, Array) or isinstance(self.second, Array):
            raise ArrayInExpressionError("Array used in expression.", 31)

    def get_all_instances(self, item):
        """Return all subcommands/commands that are type of specified item."""
        temp = []
        if isinstance(self, item):
            temp.append(self)
        temp += self.first.get_all_instances(item)
        temp += self.second.get_all_instances(item)

        return temp


class Assign(Command):
    """Assign expression to identifier."""
    def __init__(self, identifier: Identifier, expression: Expression):
        self.identifier = identifier
        self.expression = expression
        identifier.set_value_as_known()

    def get_all_containing(self, item):
        if (self.identifier.contains(item) or self.expression.contains(item)):
            return [self]
        return []

    def get_path_to(self, item):
        if self is item:
            return [self]
        elif self.identifier.get_path_to(item):
            return [self] + self.identifier.get_path_to(item)
        elif self.expression.get_path_to(item):
            return [self] + self.expression.get_path_to(item)
        return False

    def __str__(self):
        return ("assign " + str(self.expression) + " to " +
                str(self.identifier))

    def get_all_instances(self, item):
        """Return all subcommands/commands that are type of specified item."""
        temp = []
        if isinstance(self, item):
            temp.append(self)
        temp += self.identifier.get_all_instances(item)
        temp += self.expression.get_all_instances(item)

        return temp


class Read(Command):
    """Read value from user and assign it to identifier."""
    def __init__(self, identifier: Identifier):
        self.identifier = identifier
        identifier.set_value_as_known()

    def __str__(self):
        return "read(" + str(self.identifier) + ")"

    def get_all_containing(self, item):
        if (self.identifier is item):
            return [self]
        return []

    def get_path_to(self, item):
        if self is item:
            return [self]
        elif self.identifier.get_path_to(item):
            return [self] + self.identifier.get_path_to(item)
        return False

    def get_all_instances(self, item):
        """Return all subcommands/commands that are type of specified item."""
        temp = []
        if isinstance(self, item):
            temp.append(self)
        temp += self.identifier.get_all_instances(item)

        return temp


class Print(Command):
    """Print provided value to user."""

    def __init__(self, value: Value):
        value.can_be_used()
        self.value = value

    def get_all_containing(self, item):
        if (self.value.contains(item)):
            return [self]
        return []

    def get_path_to(self, item):
        if self is item:
            return [self]
        elif self.value.get_path_to(item):
            return [self] + self.value.get_path_to(item)
        return False

    def __str__(self):
        return "print(" + str(self.value) + ")"

    def get_all_instances(self, item):
        """Return all subcommands/commands that are type of specified item."""
        temp = []
        if isinstance(self, item):
            temp.append(self)
        temp += self.value.get_all_instances(item)

        return temp


class Condition:
    '''Abstraction over boolean condition.'''

    def __init__(self, first: Value, operator, second: Value):
        if (isinstance(first, Array) and isinstance(second, Variable) or 
            isinstance(second, Array) and isinstance(first, Variable)):
            raise ValueComparedWithArrayError("Can not compare.", 27)
        first.can_be_used()
        second.can_be_used()
        self.first = first
        self.operator = operator
        self.second = second


    def contains(self, item):
        if (self.first.contains(item) or self.second.contains(item)):
            return True
        return False

    def get_path_to(self, item):
        if self is item:
            return [self]
        elif self.first.get_path_to(item):
            return [self] + self.first.get_path_to(item)
        elif self.second.get_path_to(item):
            return [self] + self.second.get_path_to(item)
        return False

    def __str__(self):
        return ("condition(" + str(self.first) + " " + self.operator + " " +
                str(self.second) + ")")

    def get_all_instances(self, item):
        """Return all subcommands/commands that are type of specified item."""
        temp = []
        if isinstance(self, item):
            temp.append(self)
        temp += self.first.get_all_instances(item)
        temp += self.second.get_all_instances(item)

        return temp


class If(Command):
    """Describe simple if then (no else) statement."""
    def __init__(self, condition: Condition, block: Commands):
        self.condition = condition
        self.block = block

    def __str__(self):
        return "If(" + str(self.condition) + ")Then(commands)"

    def print_out(self, indentation=0):
        print(" " * indentation + "IF " + str(self.condition))
        print(" " * indentation + "THEN")
        self.block.print_out(indentation + 4)
        print(" " * indentation + "ENDIF")

    def get_all_containing(self, item):
        if self.condition.contains(item):
            temp = [self]
        else:
            temp = []
 
        temp += self.block.get_all_containing(item)
        return temp + []

    def get_path_to(self, item):
        if self is item:
            return [self]
        elif self.condition.get_path_to(item):
            return [self] + self.condition.get_path_to(item)
        elif self.block.get_path_to(item):
            return [self] + self.block.get_path_to(item)
        return False

    def get_all_instances(self, item):
        """Return all subcommands/commands that are type of specified item."""
        temp = []
        if isinstance(self, item):
            temp.append(self)
        temp += self.block.get_all_instances(item)
        temp += self.condition.get_all_instances(item)

        return temp

    def remove(self, item):
        self.block.remove(item)

    def iterate(self):
        for command in self.block:
            yield command.iterate()
        return self


class IfElse(Command):
    """Describe if then else statement."""
    def __init__(self, condition: Condition, block_true: Commands, block_false:
                 Commands):
        self.condition = condition
        self.block_true = block_true
        self.block_false = block_false

    def __str__(self):
        return "If(" + str(self.condition) + ")Then(commands)Else(commands)"

    def print_out(self, indentation=0):
        print(" " * indentation + "IF " + str(self.condition))
        print(" " * indentation + "THEN")
        self.block_true.print_out(indentation + 4)
        print(" " * indentation + "ELSE")
        self.block_false.print_out(indentation + 4)
        print(" " * indentation + "ENDIF")

    def get_all_containing(self, item):
        if self.condition.contains(item):
            temp = [self]
        else:
            temp = []
        temp += self.block_false.get_all_containing(item) + self.block_true.get_all_containing(item)
        return temp

    def get_path_to(self, item):
        if self is item:
            return [self]
        elif self.condition.get_path_to(item):
            return [self] + self.condition.get_path_to(item)
        elif self.block_true.get_path_to(item):
            return [self] + self.block_true.get_path_to(item)
        elif self.block_false.get_path_to(item):
            return [self] + self.block_false.get_path_to(item)
        return False

    def get_all_instances(self, item):
        """Return all subcommands/commands that are type of specified item."""
        temp = []
        if isinstance(self, item):
            temp.append(self)
        temp += self.block_true.get_all_instances(item)
        temp += self.block_false.get_all_instances(item)
        temp += self.condition.get_all_instances(item)

        return temp

    def remove(self, item):
        self.block_true.remove(item)
        self.block_false.remove(item)

    def iterate(self):
        for command in self.block_true:
            yield command.iterate()
        for command in self.block_false:
            yield command.iterate()
        return self


class While(Command):
    """Describe While loop"""

    def __init__(self, condition: Condition, block: Commands):
        self.condition = condition
        self.block = block

    def __str__(self):
        return "While(" + str(self.condition) + ")DO(commands)ENDWHILE"

    def print_out(self, indentation=0):
        print(" " * indentation + "WHILE " + str(self.condition))
        self.block.print_out(indentation + 4)
        print(" " * indentation + "ENDWHILE")

    def get_all_containing(self, item):
        if self.condition.contains(item):
            temp = [self]
        else:
            temp = []

        temp += self.block.get_all_containing(item)
        return temp + []

    def get_path_to(self, item):
        if self is item:
            return [self]
        elif self.condition.get_path_to(item):
            return [self] + self.condition.get_path_to(item)
        elif self.block.get_path_to(item):
            return [self] + self.block.get_path_to(item)
        return False

    def get_all_instances(self, item):
        """Return all subcommands/commands that are type of specified item."""
        temp = []
        if isinstance(self, item):
            temp.append(self)
        temp += self.block.get_all_instances(item)
        temp += self.condition.get_all_instances(item)

        return temp

    def remove(self, item):
        self.block.remove(item)

    def iterate(self):
        for command in self.block:
            yield command.iterate()
        return self


class DoWhile(Command):
    """Describe Do While loop"""

    def __init__(self, condition: Condition, block: Commands):
        self.condition = condition
        self.block = block

    def __str__(self):
        return "Do(commands)While(" + str(self.condition) + ")ENDDO"

    def print_out(self, indentation=0):
        print(" " * indentation + "DO")
        self.block.print_out(indentation + 4)
        print(" " * indentation + "WHILE " + str(self.condition))
        print(" " * indentation + "ENDDO")

    def get_all_containing(self, item):
        if self.condition.contains(item):
            temp = [self]
        else:
            temp = []

        temp += self.block.get_all_containing(item)
        return temp + []

    def get_path_to(self, item):
        if self is item:
            return [self]
        elif self.condition.get_path_to(item):
            return [self] + self.condition.get_path_to(item)
        elif self.block.get_path_to(item):
            return [self] + self.block.get_path_to(item)
        return False

    def get_all_instances(self, item):
        """Return all subcommands/commands that are type of specified item."""
        temp = []
        if isinstance(self, item):
            temp.append(self)
        temp += self.block.get_all_instances(item)
        temp += self.condition.get_all_instances(item)

        return temp

    def remove(self, item):
        self.block.remove(item)

    def iterate(self):
        for command in self.block:
            yield command.iterate()
        return self


class For(Command):
    """Describe For loop (counting from lower value to bigger)."""

    # TODO: recognize iterator in loop, using some dark magic.
    def __init__(self, iterator: TempIdentifier, start_value: Value, end_value: Value,
                 block: Commands):
        start_value.can_be_used()
        end_value.can_be_used()
        self.iterator = iterator
        self.start_value = start_value
        self.end_value = end_value
        self.block = block
        if self.iterator is self.start_value or self.iterator is self.end_value:
            raise NotCorrectIteratorUse("Iterator used as start or stop value",
                                       34)

    def __str__(self):
        return ("For(" + str(self.iterator) + " FROM " + str(self.start_value) +
                "TO " + str(self.end_value) + " DO commands")

    def print_out(self, indentation=0):
        print(" " * indentation + "FOR " + str(self.iterator) + " FROM " +
              str(self.start_value) + " TO " + str(self.end_value) + " DO")
        self.block.print_out(indentation)

    def get_all_containing(self, item):
        temp = self.block.get_all_containing(item)
        if (self.start_value.contains(item) or self.end_value.contains(item)):
            return temp + [self]
        return temp + []

    def get_path_to(self, item):
        if self is item:
            return [self]
        elif self.start_value.get_path_to(item):
            return [self] + self.start_value.get_path_to(item)
        elif self.end_value.get_path_to(item):
            return [self] + self.end_value.get_path_to(item)
        elif self.block.get_path_to(item):
            return [self] + self.block.get_path_to(item)
        return False

    def get_all_instances(self, item):
        """Return all subcommands/commands that are type of specified item."""
        temp = []
        if isinstance(self, item):
            temp.append(self)
        temp += self.block.get_all_instances(item)
        temp += self.start_value.get_all_instances(item)
        temp += self.end_value.get_all_instances(item)

        return temp

    def remove(self, item):
        self.block.remove(item)

    def iterate(self):
        for command in self.block:
            yield command.iterate()
        return self


class ForBackwards(Command):
    """Describe For loop (counting from lower value to bigger)."""

    def __init__(self, iterator: TempIdentifier, start_value: Value, end_value: Value,
                 block: Commands):
        start_value.can_be_used()
        end_value.can_be_used()
        self.iterator = iterator
        self.start_value = start_value
        self.end_value = end_value
        self.block = block
        if self.iterator is self.start_value or self.iterator is self.end_value:
            raise NotCorrectIteratorUse("Iterator used as start or stop value",
                                       34)

    def __str__(self):
        return ("For_backwards(" + str(self.iterator) + " FROM " + str(self.start_value) +
                "TO " + str(self.end_value) + " DO commands")

    def print_out(self, indentation=0):
        print(" " * indentation + "FOR " + str(self.iterator) + " FROM " +
              str(self.start_value) + " TO " + str(self.end_value) + " DO")
        self.block.print_out(indentation)

    def get_all_containing(self, item):
        temp = self.block.get_all_containing(item)
        if (self.start_value.contains(item) or self.end_value.contains(item)):
            return temp + [self]
        return temp + []

    def get_path_to(self, item):
        if self is item:
            return [self]
        elif self.start_value.get_path_to(item):
            return [self] + self.start_value.get_path_to(item)
        elif self.end_value.get_path_to(item):
            return [self] + self.end_value.get_path_to(item)
        elif self.block.get_path_to(item):
            return [self] + self.block.get_path_to(item)
        return False

    def get_all_instances(self, item):
        """Return all subcommands/commands that are type of specified item."""
        temp = []
        if isinstance(self, item):
            temp.append(self)
        temp += self.block.get_all_instances(item)
        temp += self.start_value.get_all_instances(item)
        temp += self.end_value.get_all_instances(item)

        return temp

    def remove(self, item):
        self.block.remove(item)

    def iterate(self):
        for command in self.block:
            yield command.iterate()
        return self
