import language

class SpecialCommand(language.Command):
    def __init__(self, variable):
        self.variable = variable

    def __str__(self):
        return "SPECIAL COMMAND: " + str(self.variable)

    def print_out(self, indendation=0):
        print(" " * indendation + str(self))


class VariableToRegisterStart(SpecialCommand):
    """When seen, assign register to a variable. It should not be used at all
    before that command is seen."""
    def __str__(self):
        return "VARIABLE TO REGISTER START: " + str(self.variable)


class VariableToRegister(SpecialCommand):
    """When seen, assign register to a variable, and load it from memory."""
    def __str__(self):
        return "VARIABLE TO REGISTER: " + str(self.variable)


class RegisterToVariable(SpecialCommand):
    """When seen, disassociate register from a variable, and save that variable
    to memory."""
    def __str__(self):
        return "VARIABLE TO MEMORY: " + str(self.variable)


class DeleteRegister(SpecialCommand):
    """When seen, eliminate data about variable from register, and don't save
    it to memory."""
    def __str__(self):
        return "VARIABLE TO MEMORY OVER: " + str(self.variable)
