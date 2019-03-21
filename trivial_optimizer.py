"""That package is supposed to eliminate basic trivial dependencies like y= 0*x
or IF x >= 0 which of course is always True. It does not analyze connections or
whatever between specific lines of code. It is simple, and it is meant to
be."""

import language


def modulo(a: int , b: int):
    if b == 0:
        return 0
    return a % b


def division(a: int, b: int):
    if b == 0:
        return 0
    return a // b


def optimize(code: language.Commands) -> language.Commands:
    """Take program block and remove trivials from it. Then return that
    program."""
    new_block = language.Commands()

    for command in code:
        new_block += trivialize_command(command)

    return new_block


def trivialize_command(command: language.Command) -> language.Commands:
    """Master interface for trivializing, concrete functions are called here
    depending on type."""
    result = language.Commands()

    if isinstance(command, language.If):
        command.block = optimize(command.block)
        triv_condition = trivialize_condition(command.condition)
        if triv_condition is True:
            result.add_block(command.block)
        elif triv_condition is False:
            pass
        elif not command.block:
            pass
        else:
            result.add_command(command)
    elif isinstance(command, language.IfElse):
        command.block_true = optimize(command.block_true)
        command.block_false = optimize(command.block_false)
        triv_condition = trivialize_condition(command.condition)
#        if (len(command.block_true) == 1 and len(command.block_false) == 1 and
#           same_meaning(command.block_true.commands[0],
#                        command.block_false.commands[0])):
#            result.add_block(command.block_true)
        if triv_condition is True:
            result.add_block(command.block_true)
        elif triv_condition is False:
            result.add_block(command.block_false)
        else:
            result.add_command(command)
    elif isinstance(command, language.While):
        command.block = optimize(command.block)
        triv_condition = trivialize_condition(command.condition)
        if triv_condition is False:
            return language.Commands()
        elif not command.block:
            pass
        else:
            result += command
    elif isinstance(command, language.DoWhile):
        command.block = optimize(command.block)
        triv_condition = trivialize_condition(command.condition)
        if triv_condition is False:
            return command.block
        elif not command.block:
            pass
        else:
            result += command
        pass
    elif isinstance(command, language.Assign):
        triv_expression = trivialize_expression(command.expression)
        command.expression = triv_expression
        result.add_command(command)
    elif isinstance(command, language.For):
        command.block = optimize(command.block)
        if command.block:
            result.add_command(command)
    elif isinstance(command, language.ForBackwards):
        command.block = optimize(command.block)
        if command.block:
            result.add_command(command)
    else:
        result.add_command(command)

    return result


def same_meaning(first: language.Command, second: language.Command):
    if (isinstance(first, language.Assign) and isinstance(second,
                                                          language.Assign) and
       first.identifier is second.identifier):
        first = first.expression
        second = second.expression
        if (isinstance(first, language.ExpressionOperation) and isinstance(second,
                                                                           language.ExpressionOperation)):
            if first.operator == second.operator and first.operator in ("*", "+"):
                if first.first == second.second and second.first == first.second:
                    return True
    return False


def trivialize_condition(condition: language.Condition):
    """Take condition and return True if it always resolves to true, False if
    it always resolves to false and condition itself if it cannot be changed.
    That function is meant to be higher abstract over conditions in
    while/for/if etc."""
    zero = language.Number(0)
    if condition.operator == "<":
        if condition.first is condition.second:
            return False
        elif (isinstance(condition.first, language.Number) and
              isinstance(condition.second, language.Number)):
            return condition.first.value < condition.second.value
    elif condition.operator == ">":
        if condition.first is condition.second:
            return False
        elif (isinstance(condition.first, language.Number) and
              isinstance(condition.second, language.Number)):
            return condition.first.value > condition.second.value
    elif condition.operator == "<=":
        if condition.first == zero:
            return True
        elif condition.first is condition.second:
            return True
        elif (isinstance(condition.first, language.Number) and
              isinstance(condition.second, language.Number)):
            return condition.first.value <= condition.second.value
    elif condition.operator == ">=":
        if condition.second == zero:
            return True
        elif condition.first is condition.second:
            return True
        elif (isinstance(condition.first, language.Number) and
              isinstance(condition.second, language.Number)):
            return condition.first.value >= condition.second.value
    elif condition.operator == "=":
        if condition.first is condition.second:
            return True
        elif (isinstance(condition.first, language.Number) and
              isinstance(condition.second, language.Number)):
            return condition.first.value == condition.second.value
    elif condition.operator == "!=":
        if condition.first is condition.second:
            return False
        elif (isinstance(condition.first, language.Number) and
              isinstance(condition.second, language.Number)):
            return condition.first.value != condition.second.value
    return condition


def trivialize_expression(expression: language.Expression) -> language.Expression:
    """Master function for trivializing expressions."""
    if isinstance(expression, language.ExpressionSingle):
        return expression
    else:
        return trivialize_expression_operation(expression)


def trivialize_expression_operation(operation: language.ExpressionOperation) -> language.Expression:
    """Take expression and try to convert it to language.ExpressionSingle.
    Return superclass Expression object for sure."""
    zero = language.Number(0)
    one = language.Number(1)
    if operation.operator == "+":
        if operation.first == zero:
            return language.ExpressionSingle(operation.second)
        elif operation.second == zero:
            return language.ExpressionSingle(operation.first)
        elif (isinstance(operation.first, language.Number) and
              isinstance(operation.second, language.Number)):
            return language.ExpressionSingle(language.Number(operation.first.value +
                                   operation.second.value))
    elif operation.operator == "-":
        if operation.first == zero:
            return language.ExpressionSingle(operation.second)
        elif operation.second == zero:
            return language.ExpressionSingle(operation.first)
        elif (isinstance(operation.first, language.Number) and
              isinstance(operation.second, language.Number)):
            return language.ExpressionSingle(language.Number(operation.first.value -
                                   operation.second.value))
    elif operation.operator == "*":
        if operation.first == one:
            return language.ExpressionSingle(operation.second)
        elif operation.second == one:
            return language.ExpressionSingle(operation.first)
        elif (isinstance(operation.first, language.Number) and
              isinstance(operation.second, language.Number)):
            return language.ExpressionSingle(language.Number(operation.first.value *
                                   operation.second.value))
        if operation.first == zero or operation.second == zero:
            return language.ExpressionSingle(zero)
    elif operation.operator == "%":
        if operation.second == zero or operation.first == zero:
            return language.ExpressionSingle(zero)
        elif (isinstance(operation.first, language.Number) and
              isinstance(operation.second, language.Number)):
            return language.ExpressionSingle(language.Number(modulo(operation.first.value,
                                   operation.second.value)))
    elif operation.operator == "/":
        if operation.second == zero or operation.first == zero:
            return language.ExpressionSingle(zero)
        elif operation.second == one:
            return language.ExpressionSingle(operation.first)
        elif (isinstance(operation.first, language.Number) and
              isinstance(operation.second, language.Number)):
            return language.ExpressionSingle(language.Number(division(operation.first.value,
                                   operation.second.value)))
    return operation
