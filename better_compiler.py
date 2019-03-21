"""The medium version, some optimisations added."""

import sys

import language
from parse import IdentifiersManager

# TODO: At the moment for loops always will execute at least once.
DEBUG = False

NEXT_FREE_MEMORY_CELL: int = 0

INDENTATION: int = 0

# A register should not be used for anything other than addressing ATM.


def print_debug(string: str):
    """Print debug line."""
    global INDENTATION
    #print(" " * 4 * INDENTATION + string, file=sys.stderr)


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

    def command_count(self):
        """Return how many commands is there already remember."""
        return len(self.commands)

    def get_code(self):
        """Return code as one string delimited with \\n."""
        to_return = ""
        for command in self.commands:
            to_return += command + "\n"

        return to_return

    def reverse(self):
        """Reverse order of commands."""
        self.commands = self.commands[::-1]

    def __iter__(self):
        return iter(self.commands)

    def __len__(self):
        return len(self.commands)

    def __add__(self, value):
        temp = MachineCode()
        temp.commands = self.commands
        temp.commands += value.commands

        return temp


class Register:
    def __init__(self, name, taken=False):
        self.name = name
        self.owner = None
        self.taken = taken
        self.contains = None
        self.former_owners = []
        self.former_values = []

    def associate(self, owner) -> MachineCode:
        """Simplest way to associate register that is not taken yet."""
        if self.owner is None:
            self.owner = owner
            self.taken = True
            print_debug("{0} gets {1}".format(str(owner), self.name))
            return MachineCode()
        else:
            raise BaseException("Register {0} is already taken by\
                                {1}".format(self.name, self.owner))

    def change_content(self, owner, value):
        """Mark that different value is stored in register now."""
        if self.owner is owner:
            self.contains = value
        else:
            raise BaseException("{0} tries to change content, it's not an\
                                owner".format(str(owner)))

    def free(self, owner) -> MachineCode:
        """Free register (if you are owner), and load back all the stuff it
        stored before (if any). Returns MachineCode object with all the
        required assembly code (if any)."""
        if self.owner is owner:
            if self.former_owners:
                print_debug("{0} sets free {1} restoring {2}".format(str(owner),
                                                   self.name,
                                                   str(self.former_owners[-1])))

                self.owner = self.former_owners.pop()
                self.contains = self.former_values.pop()
                # TODO: code
                return MachineCode()
            else:
                self.taken = False
                self.owner = None
                print_debug("{0} sets free {1}".format(str(owner),
                                                        self.name))
                return MachineCode()
        else:
            raise BaseException("{0} tries to free {1} which is not\
                                his".format(owner, self.name))

    def force_associate(self, owner) -> MachineCode:
        """Force register to be dumped and used (use it with address register
        for example."""
        result = MachineCode()
        if not self.taken:
            self.taken = True
            print_debug("{0} forces {1} without dump".format(str(owner),
                                                             self.name))
            self.owner = owner
            return result
        else:
            self.taken = True
            if self.owner is True and self.contains is True:
                print_debug("{0} force to allocate {1}, but it's not\
                            taken".format(str(owner), self.name))
                # We are forcing over A, and it's not associated with anything.
            else:
                print_debug("{0} forces {1} dumping {2}".format(str(owner),
                                                                self.name,
                                                                str(self.owner)))

            self.former_values.append(self.contains)
            self.former_owners.append(self.owner)
            self.owner = owner

            # TODO: code
            return result


def set_register_to(register: Register, value: int) -> str:
    """Set register value to known integer."""
    smart_block = MachineCode()
    while value > 11:
        # Do some smart stuff first.
        if value % 2 == 0:
            smart_block.add_command("ADD {0} {0}".format(register.name))
            value //= 2
        else:
            smart_block.add_command("INC {0}".format(register.name))
            value -= 1
    smart_block.reverse()

    normal_block = MachineCode()
    normal_block.add_command("SUB {0} {0}".format(register.name))
    for _ in range(0, value):
        normal_block.add_command("INC {0}".format(register.name))

    normal_block += smart_block
    return normal_block.get_code()


class Compiler:
    def __init__(self, program: language.Program, manager: IdentifiersManager):
        """Make those sweet low-level commands out of program."""
        self.program = program
        self.manager = manager
        # If register is False, it means it is not taken.
        self.registers = {"B": Register("B"),
                          "C": Register("C"),
                          "D": Register("D"),
                          "E": Register("E"),
                          "F": Register("F"),
                          "G": Register("G"),
                          "H": Register("H"),
                          "A": Register("A", True)}
        # Special stuff for address register.
        self.registers["A"].contains = True
        self.registers["A"].owner = True

    def get_not_associated_register(self, objects: list) -> Register:
        """Return name of register that is free, and is not associated with any of the
        objects provided. If there is no such register, its value will be
        dumped and restored after register is free."""
        # Check if there is any free register.
        for register in self.registers.items():
            if register[1].taken is False:
                return register[1]

        # Check for non associated registers.
        for register in self.registers.items():
            if register[1].contains not in objects:
                return register[1]

        raise BaseException("There is no register that is not associated!")

    def get_register_by_name(self, name: str) -> Register:
        """Return register identified by a name."""
        try:
            return self.registers[name]
        except KeyError:
            raise BaseException("There is no such register as {0}".format(name))

    def get_not_associated_register_regs(self, registers: list) -> Register:
        """Return name of register that is free, and is not associated with any of the
        objects provided. If there is no such register, its value will be
        dumped and restored after register is free."""
        # Check if there is any free register that is not in list.
        for register in self.registers.items():
            if register[1].taken is False and register[1] not in registers:
                return register[1]

        # Check for non associated registers.
        for register in self.registers.items():
            if register[1] not in registers:
                return register[1]

        raise BaseException("There is no register that is not associated!")

    def get_register_by_name(self, name: str) -> Register:
        """Return register identified by a name."""
        try:
            return self.registers[name]
        except KeyError:
            raise BaseException("There is no such register as {0}".format(name))



    def set_value_to_register(self, register_obj: Register, value: language.Value) -> str:
        """Set specified register value to value of provided language.Value."""
        global INDENTATION
        print_debug("START set {0} to {1}".format(str(value), register_obj.name))
        INDENTATION += 1

        register = register_obj.name
        to_return = ""
        if DEBUG:
            to_return += "# set " + str(value) + " to " + register + "\n"

        if isinstance(value, (language.Number, language.Variable)):
            # OPTIMIZATION CHECK
            # Check if value is already in one of registers, if it is, just copy it
            # over.
            value_register = None
            for reg in self.registers:
                # It is important that we use 'is' here, so it's exactly same
                # object.
                # TODO: dirty hack is used here, to ensure that object won't use
                # this value when it was allocated by itself.
                if self.registers[reg].contains is value:
                    value_register = self.registers[reg]

            if value_register:
                INDENTATION -= 1
                if value_register is not register_obj:
                    to_return += "COPY {0} {1}\n".format(register_obj.name,
                                                         value_register.name)
                    print_debug("STOP smart set {0} to {1} copying from {2}".format(str(value), register,
                                                                 value_register.name))
                else:
                    print_debug("STOP smart set {0} to {1}".format(str(value), register))


                return to_return

        if isinstance(value, language.Number):
            to_return += set_register_to(register_obj, value.value)

        elif isinstance(value, language.VariableBase):
            reg = self.get_register_by_name("A")
            to_return += reg.force_associate(self).get_code()
            to_return += set_register_to(reg, value.memory_cell)

            to_return += "LOAD " + register + "\n"
            to_return += reg.free(self).get_code()

        elif isinstance(value, language.ArrayCell):
            reg = self.get_register_by_name("A")
            # Temp reg trick
            # TODO: memory address of value, not value is being saved!
            temp_reg = self.get_not_associated_register_regs([reg])
            to_return += temp_reg.associate(self).get_code()
            to_return += self.get_memory_cell_value(temp_reg, value)
            temp_reg.change_content(self, None)
            to_return += reg.force_associate(self).get_code()
            to_return += "COPY " + reg.name + " " + temp_reg.name + "\n"
            reg.change_content(self, None)
            to_return += temp_reg.free(self).get_code()

            to_return += "LOAD " + register_obj.name + "\n"
            to_return += reg.free(self).get_code()

        elif isinstance(value, int):
            to_return += set_register_to(register_obj, value)
        else:
            print("Unsupported value: " + str(value))
            sys.exit(1)

        print_debug("END set {0} to {1}".format(str(value), register))
        INDENTATION -= 1

        return to_return

    def get_memory_cell_value(self, register: Register, value: language.Value) -> str:
        """Set value of register to memory cell address."""
        global INDENTATION
        print_debug("START GET MEMORY CELL OF: " + str(value))
        INDENTATION += 1
        to_return = ""
        if DEBUG:
            to_return += ("# get memory cell " + str(value) + " to " +
                          register.name +
                          "\n")
        if isinstance(value, language.Number):
            raise language.LanguageException("Number does not have address.", 36)

        elif isinstance(value, language.VariableBase):
            to_return += self.set_value_to_register(register, value.memory_cell)

        elif isinstance(value, language.ArrayCell):
            temp_reg = self.get_not_associated_register([])
            to_return += temp_reg.associate(self).get_code()
            to_return += self.set_value_to_register(temp_reg, value.index)
            temp_reg.change_content(self, value.index)
            to_return += set_register_to(register, value.array.memory_cell)

            to_return += "ADD " + register.name + " " + temp_reg.name + "\n"

            to_return += set_register_to(temp_reg, value.array.start_index)
            temp_reg.change_content(self, value.array.start_index)
            to_return += "SUB " + register.name + " " + temp_reg.name +"\n"
            to_return += temp_reg.free(self).get_code()

        if DEBUG:
            to_return += ("#END OF GETTING MEMORY CELL \n")

        INDENTATION -= 1
        print_debug("STOP GET MEMORY CELL OF: " + str(value))
        return to_return

    def increment(self, variable: language.Variable):
        global INDENTATION
        print_debug("START INCREMENT:  " + str(variable))
        INDENTATION += 1
 
        to_return = ""
        temp_reg = self.get_not_associated_register([])
        to_return += temp_reg.associate(self).get_code()
        if DEBUG:
            to_return += "# increment " + str(variable) + "\n"
        to_return += self.set_value_to_register(temp_reg, variable)
        to_return += "INC " + temp_reg.name + "\n"
        # We don't need to reaload A, cause register address did not change.
        to_return += "STORE " + temp_reg.name + "\n"
        # TODO: decrement and describe that register contains value?
        to_return += temp_reg.free(self).get_code()

        INDENTATION -= 1
        print_debug("STOP INCREMENT:  " + str(variable))
        return to_return

    def decrement(self, variable: language.Variable):
        global INDENTATION
        print_debug("START DECREMENT:  " + str(variable))
        INDENTATION += 1

        to_return = ""
        temp_reg = self.get_not_associated_register([])
        to_return += temp_reg.associate(self).get_code()
        if DEBUG:
            to_return += "# decrement " + str(variable) + "\n"
        to_return += self.set_value_to_register(temp_reg, variable)
        to_return += "DEC " + temp_reg.name + "\n"
        # We don't need to reaload A, cause register address did not change.
        to_return += "STORE " + temp_reg.name + "\n"
        # TODO: increment and describe that register contains value?
        to_return += temp_reg.free(self).get_code()

        INDENTATION -= 1
        print_debug("STOP DECREMENT: " + str(variable))
        return to_return

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
            #print(first_free_memory_cell)
            array.memory_cell = first_free_memory_cell
            first_free_memory_cell += array.length + 1

        global NEXT_FREE_MEMORY_CELL
        NEXT_FREE_MEMORY_CELL = first_free_memory_cell

    def compile(self) -> str:
        """Return ready to run machine code."""
        self.prepare()
        program_block = self.program.block

        result = MachineCode()

        for command in program_block:
            result += compile_command(command, self)

        result.add_command("HALT")

        # Check for all relative jumps and adjust.

        for index in range(0, len(result.commands)):
            splitted_command = result.commands[index].split()
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
            result.commands[index] = temp 

        to_return = result.get_code()
        return to_return


def compile_block(block: language.Commands, compiler: Compiler) -> MachineCode:
    result = MachineCode()
    for command in block:
        result += compile_command(command, compiler)

    return result


def compile_command(something: language.Command, compiler: Compiler) -> MachineCode:
    """At the moment only direct commands can be compiled using this function.
    Values, conditions etc. are meant to be compiled using manually chosen
    classes."""
    if isinstance(something, language.Assign):
        temp = AssignCompiler(something, compiler)
    elif isinstance(something, language.Print):
        temp = PrintCompiler(something, compiler)
    elif isinstance(something, language.Read):
        temp = ReadCompiler(something, compiler)
    elif isinstance(something, language.If):
        temp = IfCompiler(something, compiler)
    elif isinstance(something, language.IfElse):
        temp = IfElseCompiler(something, compiler)
    elif isinstance(something, language.While):
        temp = WhileCompiler(something, compiler)
    elif isinstance(something, language.DoWhile):
        temp = DoWhileCompiler(something, compiler)
    elif isinstance(something, language.For):
        temp = ForCompiler(something, compiler)
    elif isinstance(something, language.ForBackwards):
        temp = ForBackwardsCompiler(something, compiler)
    else:
        print("Unsupported construct: " + str(something))
        sys.exit(1)
    return temp.compile()


class AssignCompiler:
    def __init__(self, assign: language.Assign, compiler: Compiler):
        self.assign = assign
        self.compiler = compiler

    def compile(self) -> MachineCode:
        # Get value to register X.
        # Set address of identifier to register A.
        # Store register X.
        global INDENTATION
        print_debug("START: " + str(self.assign))
        INDENTATION += 1

        block = MachineCode()
        if DEBUG:
            block.add_command("# " + str(self.assign))
        # Register which keeps calculated value to save.
        if isinstance(self.assign.expression, language.ExpressionSingle):
            expression = ExpressionSingleCompiler(self.assign.expression,
                                                  self.compiler)
            block += expression.compile()
            get_register = expression.register
        elif isinstance(self.assign.expression, language.ExpressionOperation):
            expression = ExpressionOperationCompiler(self.assign.expression,
                                                     self.compiler)
            block += expression.compile()
            get_register = expression.register
        else:
            print("Unknown expression type")
            sys.exit(2)

        # Get address to temp register, than copy it to A. So taking address
        # does not use A directly (array cell needs to use it).
        address_reg = self.compiler.get_register_by_name("A")
        temp_reg = self.compiler.get_not_associated_register_regs([address_reg])

        # Memory address of identifier.
        block += temp_reg.associate(self)
        block.add_commands(self.compiler.get_memory_cell_value(temp_reg,
                                                               self.assign.identifier))
        temp_reg.change_content(self, None)
        block += address_reg.force_associate(self)

        block.add_command("COPY {0} {1}".format(address_reg.name, temp_reg.name))
        address_reg.change_content(self, temp_reg.contains)
        block += temp_reg.free(self)

        block.add_command("STORE {0}".format(get_register.name))

        # Transitive ownership.
        block += get_register.free(AssignCompiler)
        block += address_reg.free(self)

        if DEBUG:
            block.add_command("# END OF ASSIGN")

        INDENTATION -= 1
        print_debug("STOP: " + str(self.assign))
        return block


class ExpressionSingleCompiler:
    def __init__(self, expression: language.ExpressionSingle, compiler:
                 Compiler):
        self.expression = expression
        self.compiler = compiler

    def compile(self) -> MachineCode:
        """Calculate value, save it to register and set self.register to that
        register."""
        global INDENTATION
        print_debug("START: " + str(self.expression))
        INDENTATION += 1

        block = MachineCode()
        out_reg = self.compiler.get_not_associated_register([])
        # Transitive ownership.
        block += out_reg.associate(AssignCompiler)
        block.add_commands(self.compiler.set_value_to_register(out_reg,
                                                               self.expression.value))
        out_reg.change_content(AssignCompiler, self.expression.value)

        self.register = out_reg

        print_debug("START: " + str(self.expression))
        INDENTATION -= 1
        return block


class ExpressionOperationCompiler:
    # TODO: soft coded registers
    def __init__(self, expression: language.ExpressionOperation, compiler:
                 Compiler):
        self.expression = expression
        self.compiler = compiler

    def compile(self) -> MachineCode:
        """Calculate value, save it to register and set self.register to that
        register."""
        global INDENTATION
        print_debug("START: " + str(self.expression))
        INDENTATION += 1
        block = MachineCode()

        # B
        first_reg = self.compiler.get_not_associated_register([])
        block += first_reg.associate(AssignCompiler)
        block.add_commands(self.compiler.set_value_to_register(first_reg,
                                                               self.expression.first))
        first_reg.change_content(AssignCompiler, self.expression.first)
        # C
        second_reg = self.compiler.get_not_associated_register_regs([first_reg])
        block += second_reg.associate(self)
        block.add_commands(self.compiler.set_value_to_register(second_reg,
                                                               self.expression.second))
        second_reg.change_content(self, self.expression.second)

        if self.expression.operator == "+":
            block.add_command("ADD {0} {1}".format(first_reg.name,
                                                   second_reg.name))
            first_reg.change_content(AssignCompiler, None)

            block += second_reg.free(self)
            self.register = first_reg
        elif self.expression.operator == "-":
            block.add_command("SUB {0} {1}".format(first_reg.name,
                                                   second_reg.name))
            first_reg.change_content(AssignCompiler, None)

            block += second_reg.free(self)
            self.register = first_reg
        elif self.expression.operator == "*":
            # Let's assume that our base is B, and our counter is C.

            # Get additional register.
            additional_reg = self.compiler.get_not_associated_register_regs([first_reg,
                                                                    second_reg])
            block += additional_reg.associate(self)


            # If we multiply by zero, just jump over whole block zeroing result
            # register at the end.
            multiplication = MachineCode()

            # If we multiply by zero, just skip the whole procedure.
            multiplication.add_command("JZERO {0} +19".format(second_reg.name))

            multiplication.add_command("JZERO {0} +18".format(first_reg.name))


            multiplication.add_command("COPY {0} {1}".format(additional_reg.name,
                                                             second_reg.name))

            multiplication.add_command("INC {0}".format(additional_reg.name))

            multiplication.add_command("JZERO {0} +4".format(additional_reg.name))

            multiplication.add_command("COPY {0} {1}".format(additional_reg.name,
                                                             first_reg.name))

            multiplication.add_command("COPY {0} {1}".format(first_reg.name,
                                                             second_reg.name))

            multiplication.add_command("COPY {0} {1}".format(second_reg.name,
                                                             additional_reg.name))

            # Copy value of not counter to D register.
            multiplication.add_command("COPY {0} {1}".format(additional_reg.name,
                                                         first_reg.name))

            # Zero out our result.
            multiplication.add_command("SUB {0} {0}".format(first_reg.name))

            # Check if number is odd, if it is, go to naive mutliplication.
            multiplication.add_command("JODD {0} +5".format(second_reg.name))

            # We know that C is even, if we are here, double up.
            multiplication.add_command("ADD {0} {0}".format(additional_reg.name))
            multiplication.add_command("HALF {0}".format(second_reg.name))
            # Check if we should keep iterating.
            multiplication.add_command("JZERO {0} +7".format(second_reg.name))
            multiplication.add_command("JUMP -4")

            # Do it like in the good ol' days.
            multiplication.add_command("ADD {0} {1}".format(first_reg.name,
                                                        additional_reg.name))
            multiplication.add_command("DEC {0}".format(second_reg.name))
            # Check if we should keep iterating.
            multiplication.add_command("JZERO {0} +3".format(second_reg.name))
            multiplication.add_command("JUMP -8")

            # Zero out result register, use it only when we multiply by zero.
            multiplication.add_command("SUB {0} {0}".format(first_reg.name))

            first_reg.change_content(AssignCompiler, None)
            second_reg.change_content(self, None)
            additional_reg.change_content(self, None)
            block += multiplication
            block += additional_reg.free(self)
            block += second_reg.free(self)

            self.register = first_reg

        elif self.expression.operator == "/":
            # Setup and tear down is defined here, so we can calculate jumps
            # length.
            setup = MachineCode()

            # Allocate registers.
            z_reg = self.compiler.get_not_associated_register_regs([first_reg,
                                                                   second_reg])
            setup += z_reg.associate(self)

            tmp_reg = self.compiler.get_not_associated_register_regs([first_reg,
                                                                   second_reg,
                                                                   z_reg])
            setup += tmp_reg.associate(self)

            q_reg = self.compiler.get_not_associated_register_regs([first_reg,
                                                                   second_reg,
                                                                   z_reg,
                                                                   tmp_reg])
            setup += q_reg.associate(self)

            # Some stuff.
            first_reg.change_content(AssignCompiler, None)
            second_reg.change_content(self, None)
            z_reg.change_content(self, None)
            q_reg.change_content(self, None)
            tmp_reg.change_content(self, None)

            # Zero out registers.
            setup.add_command("SUB {0} {0}".format(z_reg.name))
            setup.add_command("SUB {0} {0}".format(tmp_reg.name))
            setup.add_command("SUB {0} {0}".format(q_reg.name))

            teardown = MachineCode()
            # Disallocate registers.

            teardown += q_reg.free(self) 
            teardown += tmp_reg.free(self) 
            teardown += z_reg.free(self) 
            teardown += second_reg.free(self)


            # If we got zero in b, just zero out result and return.
            division = MachineCode()
            division.add_command("JZERO {0} +2".format(second_reg.name))
            division.add_command("JUMP +3")
            division.add_command("SUB {0} {0}".format(first_reg.name))
            division.add_command("JUMP +{0}".format(str(29 + len(division) +
                                                       len(teardown))))

            division += setup


            # More checks.
            division.add_command("COPY {0} {1}".format(z_reg.name,
                                                       first_reg.name))
            division.add_command("INC {0}".format(z_reg.name))

            division.add_command("SUB {0} {1}".format(z_reg.name,
                                                      second_reg.name))

            # Exit if we can't fit even once.
            division.add_command("JZERO {0} +2".format(z_reg.name))
            division.add_command("JUMP +3")

            # This will be different for modulo!!!!!
            division.add_command("COPY {0} {1}".format(first_reg.name, z_reg.name))
            division.add_command("JUMP +{0}".format(str(len(teardown) + 22)))

            division.add_command("INC {0}".format(tmp_reg.name))


            # do
            division.add_command("ADD {0} {0}".format(tmp_reg.name))
            division.add_command("ADD {0} {0}".format(second_reg.name))
            division.add_command("COPY {0} {1}".format(z_reg.name,
                                                       second_reg.name))
            division.add_command("SUB {0} {1}".format(z_reg.name,
                                                      first_reg.name))
            # while Z == 0
            division.add_command("JZERO {0} -4".format(z_reg.name))

            division.add_command("HALF {0}".format(tmp_reg.name))
            division.add_command("ADD {0} {1}".format(q_reg.name, tmp_reg.name))
            division.add_command("HALF {0}".format(second_reg.name))
            division.add_command("SUB {0} {1}".format(first_reg.name,
                                                      second_reg.name))

            # do
            division.add_command("COPY {0} {1}".format(z_reg.name,
                                                       second_reg.name))
            division.add_command("SUB {0} {1}".format(z_reg.name,
                                                      first_reg.name))

            division.add_command("JZERO {0} +2".format(z_reg.name))
            division.add_command("JUMP +3")

            division.add_command("SUB {0} {1}".format(first_reg.name,
                                                      second_reg.name))
            division.add_command("ADD {0} {1}".format(q_reg.name, tmp_reg.name))

            division.add_command("HALF {0}".format(tmp_reg.name))
            division.add_command("HALF {0}".format(second_reg.name))
            # while tmp != 0
            division.add_command("JZERO {0} +2".format(tmp_reg.name))
            division.add_command("JUMP -9")

            # Copy result to Y
            division.add_command("COPY {0} {1}".format(first_reg.name,
                                                       q_reg.name))

            division += teardown

            block += division

            self.register = first_reg

        # TODO: Modulo is disabled too.
        elif self.expression.operator == "%":
            # Setup and tear down is defined here, so we can calculate jumps
            # length.
            setup = MachineCode()

            # Allocate registers.
            z_reg = self.compiler.get_not_associated_register_regs([first_reg,
                                                                   second_reg])
            setup += z_reg.associate(self)

            tmp_reg = self.compiler.get_not_associated_register_regs([first_reg,
                                                                   second_reg,
                                                                   z_reg])
            setup += tmp_reg.associate(self)

            q_reg = self.compiler.get_not_associated_register_regs([first_reg,
                                                                   second_reg,
                                                                   z_reg,
                                                                   tmp_reg])
            setup += q_reg.associate(self)

            # Some stuff.
            first_reg.change_content(AssignCompiler, None)
            second_reg.change_content(self, None)
            z_reg.change_content(self, None)
            q_reg.change_content(self, None)
            tmp_reg.change_content(self, None)

            # Zero out registers.
            setup.add_command("SUB {0} {0}".format(z_reg.name))
            setup.add_command("SUB {0} {0}".format(tmp_reg.name))
            setup.add_command("SUB {0} {0}".format(q_reg.name))

            teardown = MachineCode()
            # Disallocate registers.

            teardown += q_reg.free(self) 
            teardown += tmp_reg.free(self) 
            teardown += z_reg.free(self) 
            teardown += second_reg.free(self)


            # If we got zero in b, just zero out result and return.
            division = MachineCode()
            division.add_command("JZERO {0} +2".format(second_reg.name))
            division.add_command("JUMP +3")
            division.add_command("SUB {0} {0}".format(first_reg.name))
            division.add_command("JUMP +{0}".format(str(27 + len(division) +
                                                       len(teardown))))

            division += setup


            # More checks.
            division.add_command("COPY {0} {1}".format(z_reg.name,
                                                       first_reg.name))
            division.add_command("INC {0}".format(z_reg.name))

            division.add_command("SUB {0} {1}".format(z_reg.name,
                                                      second_reg.name))

            # Exit if we can't fit even once.
            division.add_command("JZERO {0} +2".format(z_reg.name))
            division.add_command("JUMP +2")

            # No copy needed here.
            division.add_command("JUMP +{0}".format(str(len(teardown) + 21)))

            division.add_command("INC {0}".format(tmp_reg.name))


            # do
            division.add_command("ADD {0} {0}".format(tmp_reg.name))
            division.add_command("ADD {0} {0}".format(second_reg.name))
            division.add_command("COPY {0} {1}".format(z_reg.name,
                                                       second_reg.name))
            division.add_command("SUB {0} {1}".format(z_reg.name,
                                                      first_reg.name))
            # while Z == 0
            division.add_command("JZERO {0} -4".format(z_reg.name))

            division.add_command("HALF {0}".format(tmp_reg.name))
            division.add_command("ADD {0} {1}".format(q_reg.name, tmp_reg.name))
            division.add_command("HALF {0}".format(second_reg.name))
            division.add_command("SUB {0} {1}".format(first_reg.name,
                                                      second_reg.name))

            # do
            division.add_command("COPY {0} {1}".format(z_reg.name,
                                                       second_reg.name))
            division.add_command("SUB {0} {1}".format(z_reg.name,
                                                      first_reg.name))

            division.add_command("JZERO {0} +2".format(z_reg.name))
            division.add_command("JUMP +3")

            division.add_command("SUB {0} {1}".format(first_reg.name,
                                                      second_reg.name))
            division.add_command("ADD {0} {1}".format(q_reg.name, tmp_reg.name))

            division.add_command("HALF {0}".format(tmp_reg.name))
            division.add_command("HALF {0}".format(second_reg.name))
            # while tmp != 0
            division.add_command("JZERO {0} +2".format(tmp_reg.name))
            division.add_command("JUMP -9")

            division += teardown

            block += division

            self.register = first_reg
        else:
            # different result register [instead of returning D we return B])
            print("Unsupported operator: " + self.expression.operator)
            sys.exit(1)

        INDENTATION -= 1
        print_debug("STOP: " + str(self.expression))
        return block


class PrintCompiler:
    def __init__(self, to_print: language.Print, compiler: Compiler):
        self.to_print = to_print
        self.compiler = compiler

    def compile(self) -> MachineCode:
        global INDENTATION
        print_debug("START: " + str(self.to_print))
        INDENTATION += 1
        block = MachineCode()
        reg = self.compiler.get_not_associated_register([])
        block += reg.associate(self)
        block.add_commands(self.compiler.set_value_to_register(reg,
                                                               self.to_print.value))
        reg.change_content(self, self.to_print.value)
        block.add_command("PUT {0}".format(reg.name))
        block += reg.free(self)

        INDENTATION -= 1
        print_debug("STOP: " + str(self.to_print))
        return block


class ReadCompiler:
    def __init__(self, read: language.Read, compiler: Compiler):
        self.read = read
        self.compiler = compiler

    def compile(self) -> MachineCode:
        global INDENTATION
        print_debug("START: " + str(self.read))
        INDENTATION += 1
        block = MachineCode()
        result_reg = self.compiler.get_not_associated_register([])
        block += result_reg.associate(self)
        address_reg = self.compiler.get_register_by_name("A")
        # Temp reg trick
        temp_reg = self.compiler.get_not_associated_register_regs([address_reg,
                                                                  result_reg])
        # TODO: it's memory, not value
        block += temp_reg.associate(self)
        block.add_commands(self.compiler.get_memory_cell_value(temp_reg,
                                                               self.read.identifier))
        temp_reg.change_content(self, None)
        block += address_reg.force_associate(self)
        block.add_command("COPY {0} {1}".format(address_reg.name, temp_reg.name))
        address_reg.change_content(self, temp_reg.contains)
        block += temp_reg.free(self)

        block.add_command("GET {0}".format(result_reg.name))
        block.add_command("STORE {0}".format(result_reg.name))
        block += address_reg.free(self)
        block += result_reg.free(self)

        INDENTATION -= 1
        print_debug("STOP: " + str(self.read))
        return block


class ConditionCompiler:
    def __init__(self, condition: language.Condition, compiler: Compiler):
        """jump_size specifies how much program has to jump, if condition is
        false."""
        self.condition = condition
        self.compiler = compiler

    def compile(self) -> MachineCode:
        global INDENTATION
        print_debug("START: " + str(self.condition))
        INDENTATION += 1
        # Compare on double subtract basis (equals, not equals).
        # Jump by two on the end is supposed to dodge initial jump in code
        # section.
        block = MachineCode()
        # E
        first_reg = self.compiler.get_not_associated_register([])
        block += first_reg.associate(self)
        # HERE IS THE PROBLEM.
        block.add_commands(self.compiler.set_value_to_register(first_reg,
                                                               self.condition.first))
        first_reg.change_content(self, None)
        # D
        second_reg = self.compiler.get_not_associated_register_regs([first_reg])
        block += second_reg.associate(self)
        block.add_commands(self.compiler.set_value_to_register(second_reg,
                                                               self.condition.second))
        second_reg.change_content(self, None)

        if self.condition.operator == "=":
            # C
            third_reg = self.compiler.get_not_associated_register_regs([first_reg,
                                                            second_reg])
            block += third_reg.associate(self)
            third_reg.change_content(self, None)
            temp = MachineCode()
            temp += third_reg.free(self)
            third_reg.associate(self)
            # a == b
            # a - b == 0 AND b - a == 0
            block.add_command("COPY {0} {1}".format(third_reg.name,
                                                    first_reg.name))
            block.add_command("SUB {0} {1}".format(first_reg.name,
                                                   second_reg.name))
            block.add_command("JZERO {0} +2".format(first_reg.name))
            block.add_command("JUMP +{0}".format(str(3 + len(temp))))

            block.add_command("SUB {0} {1}".format(second_reg.name,
                                                   third_reg.name))

            block.add_command("JZERO {0} +{1}".format(second_reg.name, str(2 +
                                                                          len(temp))))
            block += temp
        elif self.condition.operator == "!=":
            # C
            third_reg = self.compiler.get_not_associated_register_regs([first_reg,
                                                            second_reg])
            block += third_reg.associate(self)
            third_reg.change_content(self, None)
            temp = MachineCode()
            temp += third_reg.free(self)
            # a != b
            # a - b != 0 OR b - a != 0
            block.add_command("COPY {0} {1}".format(third_reg.name,
                                                    first_reg.name))
            block.add_command("SUB {0} {1}".format(first_reg.name,
                                                   second_reg.name))
            block.add_command("JZERO {0} +2".format(first_reg.name))
            # If not zero, then numbers are not equal, jump to code.
            # If check did not work, skip jumps alltogether.
 
            block.add_command("JUMP +{0}".format(str(5 + len(temp))))

            block.add_command("SUB {0} {1}".format(second_reg.name,
                                                   third_reg.name))
            block.add_command("JZERO {0} +{1}".format(second_reg.name, str(2 +
                                                                          len(temp))))
            block.add_command("JUMP +{0}".format(str(2 + len(temp))))
            block += temp

        else:
            # Smart build of stuff.
            if self.condition.operator == "<=":
                # a <= b
                # a - b = 0
                block.add_command("SUB {0} {1}".format(first_reg.name,
                                                       second_reg.name))
                block.add_command("JZERO {0} +2".format(first_reg.name))
            elif self.condition.operator == ">=":
                # b >= a
                # b - a = 0
                # Just changed order of the above.
                block.add_command("SUB {0} {1}".format(second_reg.name,
                                                       first_reg.name))
                block.add_command("JZERO {0} +2".format(second_reg.name))
            elif self.condition.operator == ">":
                # b > a
                # b >= a+1
                # Look above.
                block.add_command("INC {0}".format(second_reg.name))
                block.add_command("SUB {0} {1}".format(second_reg.name,
                                                       first_reg.name))
                block.add_command("JZERO {0} +2".format(second_reg.name))
            elif self.condition.operator == "<":
                # a < b
                # a+1 <= b
                # Look above.
                block.add_command("INC {0}".format(first_reg.name))
                block.add_command("SUB {0} {1}".format(first_reg.name,
                                                       second_reg.name))
                block.add_command("JZERO {0} +2".format(first_reg.name))

        block += first_reg.free(self)
        block += second_reg.free(self)

        INDENTATION -= 1
        print_debug("STOP: " + str(self.condition))
        return block


class IfCompiler:
    def __init__(self, if_com: language.If, compiler: Compiler):
        self.if_com = if_com
        self.compiler = compiler

    def compile(self) -> MachineCode:
        global INDENTATION
        print_debug("START: " + str(self.if_com))
        INDENTATION += 1
        to_return = MachineCode()

        condition = MachineCode()

        condition += ConditionCompiler(self.if_com.condition, self.compiler).compile()

        block = MachineCode()
        block += compile_block(self.if_com.block, self.compiler)

        # If condition returns false, the first line of code afterwards is run.
        # So we just jump over (skip) the whole block as if it never existed
        # (because code in IF should be run only when condition is true).
        condition.add_command("JUMP +" + str(len(block) + 1))

        to_return += condition
        to_return += block

        INDENTATION -= 1
        print_debug("STOP: " + str(self.if_com))
        return to_return


class IfElseCompiler:
    def __init__(self, if_else_com: language.IfElse, compiler: Compiler):
        self.if_else_com = if_else_com
        self.compiler = compiler

    def compile(self) -> MachineCode:
        global INDENTATION
        print_debug("START: " + str(self.if_else_com))
        INDENTATION += 1
        result = MachineCode()

        condition = MachineCode()
        condition += ConditionCompiler(self.if_else_com.condition,
                                                 self.compiler).compile()

        block_false = MachineCode()
        block_false += compile_block(self.if_else_com.block_false,
                                               self.compiler)

        block_true = MachineCode()
        block_true += compile_block(self.if_else_com.block_true,
                                              self.compiler)

        # If condition returns true, the second line is run.
        # So we just run block_true, but we have to add jump at the end to skip
        # block_false that's afterwards.
        block_true.add_command("JUMP +" + str(len(block_false) + 1))

        # If condition returns false, the first line is run.
        # So we jump in that line to the block_false code.
        condition.add_command("JUMP +" + str(len(block_true) + 1))

        result += condition
        result += block_true
        result += block_false

        print_debug("START: " + str(self.if_else_com))
        INDENTATION -= 1
        return result


class WhileCompiler:
    def __init__(self, while_com: language.While, compiler: Compiler):
        self.while_com = while_com
        self.compiler = compiler

    def compile(self) -> MachineCode:
        global INDENTATION
        result = MachineCode()
        print_debug("START: " + str(self.while_com))
        INDENTATION += 1
        block = self.while_com.block
        condition = self.while_com.condition

        condition_compiled = MachineCode()
        condition_compiled += ConditionCompiler(condition,
                                                self.compiler).compile()

        # After the block, jump back to checking the condition.
        block_compiled = MachineCode()
        block_compiled += compile_block(block, self.compiler)
        block_compiled.add_command("JUMP -" + str(len(block_compiled) +
                                                  len(condition_compiled) + 1))

        # If first line after condition is run, it means that condition failed.
        # So jump over the block that would be run if condition was true.
        condition_compiled.add_command("JUMP +" + str(len(block_compiled) + 1))

        result += condition_compiled
        result += block_compiled
        INDENTATION -= 1
        print_debug("STOP: " + str(self.while_com))

        return result


class DoWhileCompiler:
    def __init__(self, do_while_com: language.DoWhile, compiler: Compiler):
        self.do_while_com = do_while_com
        self.compiler = compiler

    def compile(self) -> MachineCode:
        global INDENTATION
        print_debug("START: " + str(self.do_while_com))
        INDENTATION += 1
        result = MachineCode()

        block = MachineCode()
        block += compile_block(self.do_while_com.block, self.compiler)

        condition = MachineCode()
        condition += ConditionCompiler(self.do_while_com.condition,
                                                 self.compiler).compile()
        # If condition is false, just jump out.
        condition.add_command("JUMP +2")
        # If condition is true, jump back to execution block.
        condition.add_command("JUMP -" + str(len(condition) + len(block)))

        result += block
        result += condition
        INDENTATION -= 1
        print_debug("STOP: " + str(self.do_while_com))

        return result


class ForCompiler:
    def __init__(self, for_com: language.For, compiler: Compiler):
        self.compiler = compiler
        self.for_com = for_com
        global NEXT_FREE_MEMORY_CELL
        self.for_com.iterator.memory_cell = NEXT_FREE_MEMORY_CELL
        NEXT_FREE_MEMORY_CELL += 1
        self.counter_memory_cell = NEXT_FREE_MEMORY_CELL
        NEXT_FREE_MEMORY_CELL += 1


    def compile(self) -> MachineCode:
        global INDENTATION
        print_debug("START: " + str(self.for_com))
        INDENTATION += 1
        # Let's convert for to while.
        result = MachineCode()

        #print(self.for_com.iterator)
        value_in_loop = self.for_com.iterator
        #print(id(self.for_com.iterator))

        counter = language.Variable("loop counter")
        counter.memory_cell = self.counter_memory_cell
        #print(counter)

        setup = language.Commands()

        setup.add_command(language.Assign(value_in_loop,
                                          language.ExpressionSingle(self.for_com.start_value)))

        # Correct bounds calculation.

        setup.add_command(language.Assign(counter,
                                          language.ExpressionOperation(self.for_com.end_value,
                                                                      "+",
                                                                       language.Number(1))))

        setup.add_command(language.Assign(counter,
                                          language.ExpressionOperation(counter,
                                                                      "-",
                                                                       self.for_com.start_value)))

        setup_compiled = MachineCode()

        setup_compiled += compile_block(setup, self.compiler)

        loop_body = self.for_com.block
        loop_body.add_command(language.Assign(counter,
                                              language.ExpressionOperation(counter,
                                                                          "-",
                                                                          language.Number(1))))

        loop_body.add_command(language.Assign(value_in_loop,
                                              language.ExpressionOperation(value_in_loop,
                                                                          "+",
                                                                          language.Number(1))))

        loop = language.While(language.Condition(counter, ">=",
                                                 language.Number(1)),  loop_body)

        result += setup_compiled
        result += compile_command(loop, self.compiler)

        INDENTATION -= 1
        print_debug("STOP: " + str(self.for_com))
        return result


class ForBackwardsCompiler:
    def __init__(self, for_com: language.ForBackwards, compiler: Compiler):
        self.compiler = compiler
        self.for_com = for_com
        global NEXT_FREE_MEMORY_CELL
        self.for_com.iterator.memory_cell = NEXT_FREE_MEMORY_CELL
        NEXT_FREE_MEMORY_CELL += 1
        self.counter_memory_cell = NEXT_FREE_MEMORY_CELL
        NEXT_FREE_MEMORY_CELL += 1

    def compile(self) -> str:
        # IT'S MIRROR OF NORMAL FOR case.
        # Let's convert for to while.
        result = MachineCode()
        global INDENTATION
        print_debug("START: " + str(self.for_com))
        INDENTATION += 1

        value_in_loop = self.for_com.iterator

        counter = language.Variable("loop counter")
        counter.memory_cell = self.counter_memory_cell


        setup = language.Commands()

        setup.add_command(language.Assign(value_in_loop,
                                          language.ExpressionSingle(self.for_com.start_value)))

        # Correct loop bounds
        setup.add_command(language.Assign(counter,
                                  language.ExpressionOperation(self.for_com.start_value,
                                                              "+",
                                                               language.Number(1))))

        setup.add_command(language.Assign(counter,
                                          language.ExpressionOperation(counter,
                                                                      "-",
                                                                       self.for_com.end_value)))

        setup_compiled = MachineCode()

        setup_compiled += compile_block(setup, self.compiler)

        loop_body = self.for_com.block
        loop_body.add_command(language.Assign(counter,
                                              language.ExpressionOperation(counter,
                                                                          "-",
                                                                          language.Number(1))))

        loop_body.add_command(language.Assign(value_in_loop,
                                              language.ExpressionOperation(value_in_loop,
                                                                          "-",
                                                                          language.Number(1))))

        loop = language.While(language.Condition(counter, ">=",
                                                 language.Number(1)),  loop_body)

        result += setup_compiled
        result += compile_command(loop, self.compiler)

        INDENTATION -= 1
        print_debug("STOP: " + str(self.for_com))
        return result
