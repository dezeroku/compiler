"""The simplest possible compiler, no optimizations whatsoever."""

import sys

import language
from parse import IdentifiersManager

# TODO: At the moment for loops always will execute at least once.
DEBUG = False

NEXT_FREE_MEMORY_CELL: int = 0

# A register should not be used for anything other than addressing ATM.


def increment(variable: language.Variable):
    to_return = ""
    if DEBUG:
        to_return += "# increment " + str(variable) + "\n"
    to_return += set_value_to_register("F", variable)
    to_return += "INC F\n"
    # We don't need to reaload A, cause register address did not change.
    to_return += "STORE F\n"
    return to_return


def decrement(variable: language.Variable):
    to_return = ""
    if DEBUG:
        to_return += "# decrement " + str(variable) + "\n"
    to_return += set_value_to_register("F", variable)
    to_return += "DEC F\n"
    # We don't need to reaload A, cause register address did not change.
    to_return += "STORE F\n"
    return to_return


def get_memory_cell_value(register: str, value: language.Value) -> str:
    """Set value of register to memory cell address."""
    to_return = ""
    if DEBUG:
        to_return += ("# get memory cell " + str(value) + " to " + register +
                      "\n")
    if isinstance(value, language.Number):
        raise language.LanguageException("Number does not have address.", 36)

    elif isinstance(value, language.Variable):
        to_return += set_value_to_register(register, value.memory_cell)

    elif isinstance(value, language.ArrayCell):
        # Changing order of two below operations did the job.
        to_return += set_value_to_register("G", value.index)
        to_return += set_register_to(register, value.array.memory_cell)
        to_return += "ADD " + register + " G\n"

        to_return += set_register_to("G", value.array.start_index)
        to_return += "SUB " + register + " G\n"

    if DEBUG:
        to_return += ("#END OF GETTING MEMORY CELL \n")

    return to_return
 

def set_value_to_register(register: str, value: language.Value) -> str:
    """Set specified register value to value of provided language.Value."""
    to_return = ""
    if DEBUG:
        to_return += "# set " + str(value) + " to " + register + "\n"
    if isinstance(value, language.Number):
        to_return += set_register_to(register, value.value)
    elif isinstance(value, language.VariableBase):
        to_return += set_register_to("A", value.memory_cell)
        to_return += "LOAD " + register + "\n"
    elif isinstance(value, language.ArrayCell):
        #memory_address_of_array = value.array.memory_cell
        to_return += get_memory_cell_value("A", value)
        #to_return += set_value_to_register("F", value.index)
        #to_return += set_register_to("A", memory_address_of_array)
        #to_return += "ADD A F\n"
        to_return += "LOAD " + register + "\n"
    elif isinstance(value, int):
        to_return += set_register_to(register, value)
    else:
        print("Unsupported value: " + str(value))
        sys.exit(1)

    return to_return


class MachineCode:
    """Represent some lines of code ready to run on machine."""
    def __init__(self):
        self.commands = []

    def add_command(self, string):
        """Add compiled command (no \\n at the end is assumed)."""
        self.commands.append(string)

    def add_commands(self, string):
        """Add string of compiled commands (delimited with \\n)."""
        commands_temp = string.split("\n")
        commands = []
        for command in commands_temp:
            if command != "":
                commands.append(command)
        for command in commands:
            self.commands.append(command)

    def command_count(self, string):
        """Return how many commands is there already remember."""
        return len(self.commands)

    def get_code(self):
        """Return code as one string delimited with \\n."""
        to_return = ""
        for command in self.commands:
            to_return += command + "\n"

        return to_return

    def __iter__(self):
        return iter(self.commands)

    def __len__(self):
        return len(self.commands)

    def __add__(self, value):
        temp = MachineCode()
        temp.commands = self.commands
        temp.commands += value.commands

        return temp


def set_register_to(register: str, value: int) -> str:
    to_return = ""
    to_return += "SUB " + register + " " + register + "\n"
    for _ in range(0, value):
        to_return += "INC " + register + "\n"
    return to_return


def compile_block(block: language.Commands) -> str:
    to_return = ""
    for command in block:
        to_return += compile_command(command)

    return to_return


def compile_command(something) -> str:
    """At the moment only direct commands can be compiled using this function.
    Values, conditions etc. are meant to be compiled using manually chosen
    classes."""
    if isinstance(something, language.Assign):
        temp = AssignCompiler(something)
    elif isinstance(something, language.Print):
        temp = PrintCompiler(something)
    elif isinstance(something, language.Read):
        temp = ReadCompiler(something)
    elif isinstance(something, language.If):
        temp = IfCompiler(something)
    elif isinstance(something, language.IfElse):
        temp = IfElseCompiler(something)
    elif isinstance(something, language.While):
        temp = WhileCompiler(something)
    elif isinstance(something, language.DoWhile):
        temp = DoWhileCompiler(something)
    elif isinstance(something, language.For):
        temp = ForCompiler(something)
    elif isinstance(something, language.ForBackwards):
        temp = ForBackwardsCompiler(something)
    else:
        print("Unsupported construct: " + str(something))
        sys.exit(1)
    return temp.compile()


class Compiler:
    def __init__(self, program: language.Program, manager: IdentifiersManager):
        self.program = program
        self.manager = manager

    def prepare(self):
        """Replace all vairable with location in memory etc."""
        variables = list(self.manager.variables.values())
        for index in range(0, len(variables)):
            variables[index].memory_cell = index

        first_free_memory_cell = len(variables)
        arrays = list(self.manager.arrays.values())
        # TODO: that way of setting memory for an array, does not think about
        # relative indexing (we basically believe that every array is indexed
        # from zero, what's not true).
        for array in arrays:
            print(first_free_memory_cell)
            array.memory_cell = first_free_memory_cell
            first_free_memory_cell += array.length

        global NEXT_FREE_MEMORY_CELL
        NEXT_FREE_MEMORY_CELL = first_free_memory_cell

    def compile(self) -> str:
        """Return ready to run machine code."""
        self.prepare()
        to_return = ""
        program_block = self.program.block

        for command in program_block:
            to_return += compile_command(command)

        to_return += "HALT"

        # Check for all relative jumps and adjust.

        splitted = to_return.split("\n")
        for index in range(0, len(splitted)):
            splitted_command = splitted[index].split()
            if splitted_command[0] == "JUMP":
                jump_value = int(splitted_command[1])
                if jump_value < 0:
                    splitted_command[1] = str(index + jump_value)
                if splitted_command[1][0] == "+":
                    splitted_command[1] = str(index + jump_value)
            elif splitted_command[0] in ("JZERO", "JODD"):
                jump_value = int(splitted_command[2])
                if jump_value < 0:
                    splitted_command[2] = str(index + jump_value)
                if splitted_command[2][0] == "+":
                    splitted_command[2] = str(index + jump_value)


            temp = ""
            for subcomm in splitted_command:
                temp += subcomm + " "
            splitted[index] = temp 

            splitted[index] += "\n"

        to_return = "".join(splitted)
        return to_return


class AssignCompiler:
    def __init__(self, assign: language.Assign):
        self.assign = assign

    def compile(self) -> str:
        to_return = ""
        if DEBUG:
            to_return += "# " + str(self.assign) + "\n"
        # Register which keeps calculated value to save.
        get_register = "B"
        if isinstance(self.assign.expression, language.ExpressionSingle):
            expression = ExpressionSingleCompiler(self.assign.expression)
            to_return += expression.compile()
            get_register = expression.register
        elif isinstance(self.assign.expression, language.ExpressionOperation):
            expression = ExpressionOperationCompiler(self.assign.expression)
            to_return += expression.compile()
            get_register = expression.register
        elif isinstance(self.assign.expression, (language.VariableBase)):
            to_return += set_register_to("A", self.assign.expression.value)
            to_return += "LOAD B\n"
            get_register = "B"
        else:
            print("ERR")
            sys.exit(2)

        to_return += get_memory_cell_value("F", self.assign.identifier)

        to_return += "COPY A F\n"
        to_return += "STORE " + get_register + "\n"
        if DEBUG:
            to_return += "# END OF ASSIGN\n"
        return to_return


class ExpressionSingleCompiler:
    def __init__(self, expression: language.ExpressionSingle):
        self.expression = expression

    def compile(self) -> str:
        """Calculate value, save it to register and set self.register to that
        register."""
        to_return = ""
        to_return += set_value_to_register("B", self.expression.value)
        self.register = "B"
        return to_return


class ExpressionOperationCompiler:
    def __init__(self, expression: language.ExpressionOperation):
        self.expression = expression

    def compile(self) -> str:
        """Calculate value, save it to register and set self.register to that
        register."""
        to_return = ""

        to_return += set_value_to_register("C", self.expression.second)
        to_return += set_value_to_register("B", self.expression.first)

        # TODO: implement DIV and MOD
        if self.expression.operator == "+":
            to_return += "ADD B C\n"

            self.register = "B"
        elif self.expression.operator == "-":
            to_return += "SUB B C\n"

            self.register = "B"
        elif self.expression.operator == "*":
            # TODO: implement multiplication with logaritmic complexity.

            # If we multiply by zero, just jump over whole block zeroing result
            # register at the end.
            to_return += "JZERO C +6\n"

            to_return += "COPY D B\n"
            to_return += "DEC C\n"
            to_return += "JZERO C +4\n"
            to_return += "ADD B D\n"
            to_return += "JUMP -3\n"

            # This is called only when we multiply by zero.
            to_return += "SUB B B\n"

            self.register = "B"
        elif self.expression.operator == "/":
            # TODO: implement division with logaritmic complexity.

            # The whole problem is fact, that if we keep subtracting second
            # value from first, we will reach the point where register value
            # equals zero. Then we don't know if the rest is zero, or was just
            # eaten by the subtract operation (min(a-b, 0)).

            # In our implementation:
            # a < b (we know that b is at least 1, by definition)
            # a - b = 0 AND b - a != 0

            # - But if it works one time and b is smaller every iteration then we
            # get infinite loop, right?
            # - Well, yeah...

            # Soo, let it go the other way.
            # We loop until not b > a.


            # - But it looks same!
            # - Yeah, but it will work different, just look.

            # So until not b > a (remember that b is at least 1, by definition)
            # NOT(b - a != 0 AND a - b = 0)
            # By de'Morgane
            # b - a = 0 OR a - b != 0

            # - If at least one of these conditions is true, it means you are
            # free to finish dividing.

            # - It does not work with e.g. 4/4, cause b - a = 0 is true for
            # that case, but we get 0 as a result.
            # - Hmm, let me try one more time.

            # We stop looping when b > a, right?
            # So if b > a is true, jump out of loop, else loop one more time.
            # So AGAIN:
            # b > a in our case, if and only if
            # b - a != 0 AND a - b = 0
            # If we look closer, it's obvious that it is not infinite loop.
            # With every iteration a is smaller, but b is same, so eventually
            # a - b = 0 will have to be true (remember that b is at least 1 by
            # definition).

            # Prepare incrementing register.
            to_return += "SUB D D\n"

            # B - a
            # C - b

            divide_loop = MachineCode()

            divide_loop.add_command("COPY E B")
            divide_loop.add_command("COPY F C")

            divide_loop.add_command("SUB E C")  # E - C = a - b
            divide_loop.add_command("JZERO E +2")
            # If a - b != 0, just loop next time.
            divide_loop.add_command("JUMP +4")

            divide_loop.add_command("SUB F B")  # F - B = b - a
            # By now we know that a - b = 0, so if b - a != 0 finish dividing.
            divide_loop.add_command("JZERO F +2")

            # Finish the loop (additional +1 to jump over iterator jump).
            divide_loop.add_command("JUMP +4")

            # We can fit one more value, increment counter.
            divide_loop.add_command("INC D")
            # Subtract value to keep track of where we are.
            divide_loop.add_command("SUB B C")

            # Compose final code.

            # If we divide by zero, just jump over the whole procedure (result
            # register value is zeroed by now). We jump over block and not
            # apparent iterator.
            to_return += "JZERO C +" + str(len(divide_loop) + 2) + "\n"

            to_return += divide_loop.get_code()

            # Keep looping!
            to_return += "JUMP -" + str(len(divide_loop)) + "\n"


            self.register = "D"
        elif self.expression.operator == "%":
            # Modulo is actually dividing, we just return different register
            # afterwards.

            # Copy-Paste's Method (with removed comments)
            # We need to zero out B register if we modulo by zero (by
            # definition).

            # B - a
            # C - b

            divide_loop = MachineCode()

            divide_loop.add_command("COPY E B")
            divide_loop.add_command("COPY F C")

            divide_loop.add_command("SUB E C")  # E - C = a - b
            divide_loop.add_command("JZERO E +2")
            # If a - b != 0, just loop next time.
            divide_loop.add_command("JUMP +4")

            divide_loop.add_command("SUB F B")  # F - B = b - a
            # By now we know that a - b = 0, so if b - a != 0 finish dividing.
            divide_loop.add_command("JZERO F +2")

            # Finish the loop (additional +2 to jump over iterator jump, and
            # zeroing in case we modulo by zero.).
            divide_loop.add_command("JUMP +4")

            # Subtract value to keep track of where we are.
            divide_loop.add_command("SUB B C")

            # Compose final code.

            # If we divide by zero, just jump over the whole procedure (result
            # register value is zeroed by now). We jump over block and not
            # apparent iterator.
            to_return += "JZERO C +" + str(len(divide_loop) + 2) + "\n"

            to_return += divide_loop.get_code()

            # Keep looping!
            to_return += "JUMP -" + str(len(divide_loop)) + "\n"
            to_return += "SUB B B\n"

            self.register = "B"
        else:
            # different result register [instead of returning D we return B])
            print("Unsupported operator: " + self.expression.operator)
            sys.exit(1)

        return to_return


class PrintCompiler:
    def __init__(self, to_print: language.Print):
        self.to_print = to_print

    def compile(self) -> str:
        to_return = ""
        to_return += set_value_to_register("G", self.to_print.value)

        to_return += "PUT G\n"
        return to_return


class ReadCompiler:
    def __init__(self, read: language.Read):
        self.read = read

    def compile(self) -> str:
        to_return = ""
        to_return += get_memory_cell_value("A", self.read.identifier)
        to_return += "GET B\n"
        to_return += "STORE B\n"

        return to_return


class ConditionCompiler:
    def __init__(self, condition: language.Condition):
        """jump_size specifies how much program has to jump, if condition is
        false."""
        self.condition = condition

    def compile(self) -> str:
        # Compare on double subtract basis (equals, not equals).
        # Jump by two on the end is supposed to dodge initial jump in code
        # section.
        to_return = ""
        to_return += set_value_to_register("E", self.condition.first)
        to_return += set_value_to_register("D", self.condition.second)
        if self.condition.operator == "<=":
            # a <= b
            # a - b = 0
            to_return += "SUB E D\n"
            to_return += "JZERO E +" + str(2) + "\n"
        elif self.condition.operator == ">=":
            # a >= b
            # b - a = 0
            to_return += "SUB D E\n"
            to_return += "JZERO D +" + str(2) + "\n"
        else:

            if self.condition.operator == "=":
                # a == b
                # a - b == 0 AND b - a == 0
                to_return += "COPY C E\n"
                to_return += "SUB E D\n"
                to_return += "JZERO E +" + str(2) + "\n"
                to_return += "JUMP +" + str(3) + "\n"

                to_return += "SUB D C\n"
                to_return += "JZERO D +" + str(2) + "\n"
            elif self.condition.operator == "!=":
                # a != b
                # a - b != 0 OR b - a != 0
                to_return += "COPY C E\n"
                to_return += "SUB E D\n"
                to_return += "JZERO E +" + str(2) + "\n"
                # If not zero, then numbers are not equal, jump to code.
                # If check did not work, skip jumps alltogether.
                to_return += "JUMP +" + str(5) + "\n"

                to_return += "SUB D C\n"
                to_return += "JZERO D +" + str(2) + "\n"
                to_return += "JUMP +" + str(2) + "\n"
            elif self.condition.operator == ">":
                # a > b
                # b - a = 0 AND a - b != 0
                to_return += "COPY C D\n"
                to_return += "SUB D E\n"
                to_return += "JZERO D +" + str(2) + "\n"
                to_return += "JUMP +" + str(4) + "\n"

                to_return += "SUB E C\n"
                to_return += "JZERO E +" + str(2) + "\n"
                to_return += "JUMP +" + str(2) + "\n"
            elif self.condition.operator == "<":
                # a < b
                # a - b = 0 AND b - a != 0
                to_return += "COPY C E\n"
                to_return += "SUB E D\n"
                to_return += "JZERO E +" + str(2) + "\n"
                to_return += "JUMP +" + str(4) + "\n"

                to_return += "SUB D C\n"
                to_return += "JZERO D +" + str(2) + "\n"
                to_return += "JUMP +" + str(2) + "\n"

        return to_return


class IfCompiler:
    def __init__(self, if_com: language.If):
        self.if_com = if_com

    def compile(self) -> str:
        to_return = ""

        block = MachineCode()
        block.add_commands(compile_block(self.if_com.block))

        condition = MachineCode()

        condition.add_commands(ConditionCompiler(self.if_com.condition).compile())

        # If condition returns false, the first line of code afterwards is run.
        # So we just jump over (skip) the whole block as if it never existed
        # (because code in IF should be run only when condition is true).
        condition.add_command("JUMP +" + str(len(block) + 1))

        to_return += condition.get_code()
        to_return += block.get_code()

        return to_return


class IfElseCompiler:
    def __init__(self, if_else_com: language.IfElse):
        self.if_else_com = if_else_com

    def compile(self) -> str:
        to_return = ""

        block_false = MachineCode()
        block_false.add_commands(compile_block(self.if_else_com.block_false))

        block_true = MachineCode()
        block_true.add_commands(compile_block(self.if_else_com.block_true))

        # If condition returns true, the second line is run.
        # So we just run block_true, but we have to add jump at the end to skip
        # block_false that's afterwards.
        block_true.add_command("JUMP +" + str(len(block_false) + 1))

        condition = MachineCode()
        condition.add_commands(ConditionCompiler(self.if_else_com.condition).compile())

        # If condition returns false, the first line is run.
        # So we jump in that line to the block_false code.
        condition.add_command("JUMP +" + str(len(block_true) + 1))

        to_return += condition.get_code()
        to_return += block_true.get_code()
        to_return += block_false.get_code()

        return to_return


class WhileCompiler:
    def __init__(self, while_com: language.While):
        self.while_com = while_com

    def compile(self) -> str:
        to_return = ""
        block = self.while_com.block
        condition = self.while_com.condition

        condition_compiled = MachineCode()
        condition_compiled.add_commands(ConditionCompiler(condition).compile())

        # After the block, jump back to checking the condition.
        block_compiled = MachineCode()
        block_compiled.add_commands(compile_block(block))
        block_compiled.add_command("JUMP -" + str(len(block_compiled) +
                                                  len(condition_compiled) + 1))

        # If first line after condition is run, it means that condition failed.
        # So jump over the block that would be run if condition was true.
        condition_compiled.add_command("JUMP +" + str(len(block_compiled) + 1))

        to_return += condition_compiled.get_code()
        to_return += block_compiled.get_code()

        return to_return


class DoWhileCompiler:
    def __init__(self, do_while_com: language.DoWhile):
        self.do_while_com = do_while_com

    def compile(self) -> str:
        to_return = ""

        block = MachineCode()
        block.add_commands(compile_block(self.do_while_com.block))

        condition = MachineCode()
        condition.add_commands(ConditionCompiler(self.do_while_com.condition).compile())
        # If condition is false, just jump out.
        condition.add_command("JUMP +2")
        # If condition is true, jump back to execution block.
        condition.add_command("JUMP -" + str(len(condition) + len(block) + 1))

        to_return += block.get_code()
        to_return += condition.get_code()

        return to_return


class ForCompiler:
    def __init__(self, for_com: language.For):
        self.for_com = for_com
        global NEXT_FREE_MEMORY_CELL
        self.iterator_memory_cell = NEXT_FREE_MEMORY_CELL
        NEXT_FREE_MEMORY_CELL += 1
        self.counter_memory_cell = NEXT_FREE_MEMORY_CELL
        NEXT_FREE_MEMORY_CELL += 1



    def compile(self) -> str:
        to_return = ""

        value_in_loop = self.for_com.iterator
        value_in_loop.memory_cell = self.iterator_memory_cell

        counter = language.Variable("loop counter")
        counter.memory_cell = self.counter_memory_cell

        setup = MachineCode()

        # Assign with arraycells included is what causes For to break.

        # Assign correct start value to iterator.
        # FULL MANUAL

        setup.add_commands(set_value_to_register("H", self.for_com.start_value))
        setup.add_commands(set_register_to("A", self.iterator_memory_cell))
        setup.add_command("STORE H")

        # Give counter required value.
        # FULL MANUAL
        setup.add_commands(set_value_to_register("H", self.for_com.start_value))
        setup.add_commands(set_value_to_register("G", self.for_com.end_value))
        setup.add_command("SUB G H")
        setup.add_command("INC G")
        setup.add_command("INC G")
        setup.add_commands(set_register_to("A", self.counter_memory_cell))
        setup.add_command("STORE G")

        condition = MachineCode()

        condition.add_commands(decrement(counter))
        condition.add_commands(set_value_to_register("H", counter))
        #condition.add_command("PUT H")

        block = MachineCode()
        block.add_commands(compile_block(self.for_com.block))
        block.add_commands(increment(value_in_loop))
        block.add_command("JUMP -" + str(len(block) + len(condition) + 1))

        # Jump out of the loop.
        condition.add_command("JZERO H +" + str(len(block) + 1))

        to_return += setup.get_code()
        to_return += condition.get_code()
        to_return += block.get_code()

        return to_return


class ForBackwardsCompiler:
    def __init__(self, for_com: language.ForBackwards):
        self.for_com = for_com
        global NEXT_FREE_MEMORY_CELL
        self.iterator_memory_cell = NEXT_FREE_MEMORY_CELL
        NEXT_FREE_MEMORY_CELL += 1
        self.counter_memory_cell = NEXT_FREE_MEMORY_CELL
        NEXT_FREE_MEMORY_CELL += 1



    def compile(self) -> str:
        to_return = ""

        value_in_loop = self.for_com.iterator
        value_in_loop.memory_cell = self.iterator_memory_cell

        counter = language.Variable("loop counter")
        counter.memory_cell = self.counter_memory_cell

        setup = MachineCode()

        # Assign with arraycells included is what causes For to break.

        # Assign correct start value to iterator.
        # FULL MANUAL

        setup.add_commands(set_value_to_register("H", self.for_com.start_value))
        setup.add_commands(set_register_to("A", self.iterator_memory_cell))
        setup.add_command("STORE H")

        # Give counter required value.
        # FULL MANUAL
        setup.add_commands(set_value_to_register("H", self.for_com.end_value))
        setup.add_commands(set_value_to_register("G", self.for_com.start_value))
        setup.add_command("SUB G H")
        setup.add_command("INC G")
        setup.add_command("INC G")
        setup.add_commands(set_register_to("A", self.counter_memory_cell))
        setup.add_command("STORE G")

        condition = MachineCode()

        condition.add_commands(decrement(counter))
        condition.add_commands(set_value_to_register("H", counter))
        #condition.add_command("PUT H")

        block = MachineCode()
        block.add_commands(compile_block(self.for_com.block))
        block.add_commands(decrement(value_in_loop))
        block.add_command("JUMP -" + str(len(block) + len(condition) + 1))

        # Jump out of the loop.
        condition.add_command("JZERO H +" + str(len(block) + 1))

        to_return += setup.get_code()
        to_return += condition.get_code()
        to_return += block.get_code()

        return to_return
