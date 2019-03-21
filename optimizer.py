"""Package for analysis of parsed code, and finding connections.
THAT DOCUMENTATION IS OBSOLETE (like in real project, huh?)"""

# For compile/run at compilation time.
import subprocess
import re
import multiprocessing
import copy

import timeout_decorator

import language
import parse
import trivial_optimizer
import optimizer_stuff

# TODO: not sure whether to use better or best here.
from best_compiler import Compiler
from compilator import CompilationManager

DEBUG = False


def run_parsed_code_and_get_results(code: language.Commands, manager: parse.IdentifiersManager):
    program = language.Program()
    program.set_block(code)

    compiler = CompilationManager(Compiler, False, False)

    try:
        machine_code = compiler.compile(program, manager)
    except:
        return False

    with open(".test_file_compile", "w") as test_file:
        test_file.write(machine_code)
    result = subprocess.run(["./maszyna_rejestrowa/maszyna-rejestrowa-cln",
                             ".test_file_compile"],
                            capture_output=True)
    result = result.stdout.decode("utf-8")
    result = result.split("\n")
    # Take cost out of it.
    cost_catcher = re.compile("[0-9]+")
    cost = int(cost_catcher.findall(result[-2])[0])

    result = result[3:-2]
    result = list(map(lambda x: x[2:], result))
    return (result, cost)


# If variable has register field set, it means it is register optimized.

class SpecialCommand(language.Command):
    """Special command inserted by optimizer."""
    pass


class Symbol:
    """Just unique way to present string or whatever."""
    def __init__(self, sth):
        self.sth = sth

    def __str__(self):
        return str(self.sth)

    def __hash__(self):
        return id(self)


class WrapCommand:
    """Wrap object with basic command string."""
    def __init__(self, obj, command: str):
        self.obj = obj
        self.command = command

    def __str__(self):
        return str(self.command) + "(" + str(self.obj) + ")"


class WrapAround:
    """Wrap object with it's order number."""
    def __init__(self, obj, number: int):
        self.obj = obj
        self.number = number

    def get_object(self):
        return self.obj

    def get_number(self):
        return self.number

    def __str__(self):
        return str(self.obj) + "_" + str(self.number)

    def __eq__(self, item):
        if self.obj == item.obj and self.number == item.number:
            return True

        return False

    def __hash__(self):
        return id(self)


def remove_unused_variables(code, manager):
    # Remove all non used variables.
    check = False
    how_many = stats_variables(code, manager)
    for key in how_many:
        if how_many[key] == 0:
            check = True
            del manager.variables[key]
            ##print("Unused variable: " + key)
    return check


def remove_unused_arrays(code, manager):
    # Remove all non used arrays.
    check = False
    how_many = stats_arrays(code, manager)
    for key in how_many:
        if how_many[key] == 0:
            check = True
            del manager.arrays[key]
            #print("Unused array: " + key)
    return check


def remove_only_assigns(code, manager):
    to_remove = []
    check = False
    for key in manager.variables:
        val = manager.variables[key]
        using = code.get_all_containing(val)
        # Get all Assigns containing that object.
        using_assign = list(filter(lambda x: isinstance(x, language.Assign) or
                                   isinstance(x, language.Read),
                       code.get_all_containing(val)))
        assigned_to = list(filter(lambda x: x.identifier is val, using_assign))
        if len(using) == len(assigned_to):
            # It means that variable is unnecessary.
            if len(list(filter(lambda x: isinstance(x, language.Read), using))) == 0:
                check = True
                to_remove.append(key)
            for temp in using:
                # WE DON'T REMOVE READs.
                if not isinstance(temp, language.Read):
                    #print("Removing: " + str(temp))
                    code.remove(temp)

    for key in to_remove:
            del manager.variables[key]

    return check


def stats_variables(code, manager):
    how_many = {}
    for key in manager.variables.keys():
        how_many[key] = len(code.get_all_containing(manager.variables[key]))

    return how_many


def stats_arrays(code, manager):
    how_many = {}
    for key in manager.arrays.keys():
        how_many[key] = len(code.get_all_containing(manager.arrays[key]))

    return how_many


def wrap_array_cells(code, manager):
    return False
    check = False
    for key in manager.arrays:
        val = manager.arrays[key]
        values = code.get_all_containing(val)
        if wrap(code, manager, values):
            check = True

    return check


def wrap_variables(code, manager):
    values = code.get_all_instances(language.Variable)

    return wrap(code, manager, values)

def wrap(code, manager, values):
    check = False
    #code.print_out()
    for val in values:
        #print(val)

        # Get all variables uses.
        usage = code.get_all_containing(val)

        # If there is such use that variable is assigned on the right, skip
        # that variable altogether.
        assign = list(filter(lambda x: isinstance(x, language.Assign) or
                        isinstance(x, language.Read), usage))

        proceed = True
        for temp in assign:
            if temp.identifier is not val:
                proceed = False
                break

        if not proceed:
            usage=assign


        to_merge = []
        for index in range(0, len(usage)-1):
            # Check pairs of operations (if they can be merged somehow.)
            if not isinstance(usage[index], (language.Assign, language.Print)):
                continue
            first = code.get_path_to(usage[index])
            second = code.get_path_to(usage[index+1])
            if first[:-1] == second[:-1]:
                # Path to the operations (except THE operation) is same, they
                # can be merged.
                to_merge.append((first, second, val))
        ##print(to_merge)
        if merge(code, to_merge):
            check = True
        ##print(usage)

    return check


def merge(code, to_merge):
    check = False
    for pair in to_merge:
        first = pair[0][-1]
        second = pair[1][-1]
        val = pair[2]
        if isinstance(first, language.Assign):
            if isinstance(first.expression, language.ExpressionSingle):
                if isinstance(first.expression.value, language.VariableBase):
                    # TODO: this is dangerous moment
                    continue

                elif not isinstance(first.expression.value, language.Number):
                    continue

                if isinstance(second, language.Print):
                    check = True
                    second.value = first.expression.value
                if isinstance(second, language.IfElse):
                    check = True
                    if second.condition.first.contains(val):
                        second.condition.first = first.expression.value
                    elif second.condition.second.contains(val):
                        second.condition.second = first.expression.value
                if isinstance(second, language.Assign):
                    if isinstance(second.expression,
                                  language.ExpressionSingle):
                        if second.expression.value.contains(val):
                            second.expression.value = first.expression.value
                            check = True
                    elif isinstance(second.expression,
                                    language.ExpressionOperation):
                        # TODO:
                        if first.identifier is val and second.expression.first is val:
                            second.expression.first = first.expression.value
                            #print(first)
                            #print(second)
                            check = True
                        elif first.identifier is val and second.expression.second is val:
                            second.expression.second = first.expression.value
                            check = True
                    pass

    return check


def turbo_variables(code, manager):
    turbo = []
    variables_popularity = stats_variables(code, manager)
    try:
        keys = list(variables_popularity.keys())
        values = list(variables_popularity.values())
        rank = sorted(zip(values, keys), key=lambda x: x[0])
        if manager.variables:
            manager.variables[rank[0][1]].register = "H"
            turbo.append(rank[0][1])
    #        if len(manager.variables) > 1:
    #            manager.variables[rank[1][1]].register = "G"
    #            turbo.append(rank[1][1])
    except ValueError:
        # No variable whatsoever.
        pass
    #print("TURBO VARIABLES: " + str(turbo))


def solve_at_compile_time(code, manager, timeout: int):
    """Simple wrapper with timeout for compile_time_func."""
    manager_backup = copy.deepcopy(manager)
    for key in manager.arrays:
        manager_backup.arrays[key] = manager.arrays[key]
    for key in manager.variables:
        manager_backup.variables[key] = manager.variables[key]

    try:
        return solve_at_compile_time_func(code, manager_backup)
    except TimeoutError:
        #print("Solving at compile-time TIMEOUT")
        return code


@timeout_decorator.timeout(10, timeout_exception=TimeoutError)
def solve_at_compile_time_func(code, manager):
    """If program does not contain any Reads, compile and run it at
    compilation-time, return program that only outputs results."""
    reads = code.get_all_instances(language.Read)
    ##print(reads)
    if reads:
        print("We got READ here, nothing special.")
        return code
        pass
        # That's probably complicated, run away.
    else:
        print("Without READs, try to solve at compile time:")
        # Compile and run and do magic.
        # We will use better_compiler, not best, because I trust it more in
        # this case.
        output, cost = run_parsed_code_and_get_results(code, manager)
        #print(cost)
        if output:
            # Compilation and running went good.
            optimised = language.Commands()
            #print(output)
            for temp in output:
                optimised.add_command(language.Print(language.Number(int(temp))))

            _, optimised_cost = run_parsed_code_and_get_results(optimised,
                                                                manager)
            print("Solved at runtime")
            print("Cost: " + str(cost) + " vs " + str(optimised_cost))
            if optimised_cost < cost:
                #code.commands = optimised.commands
                print("Optimised code is about " +
                      str(round(cost/optimised_cost*100, 2))
                     + " percent faster.")
                return optimised
            elif optimised_cost == cost:
                print("No difference in speed between normal and optimised.")
                print("Falling back to normal.")
            else:
                print("Normal code is faster")
                print("Optimised code would be about " +
                      str(round(optimised_cost/cost*100, 2))
                     + " percent slower.")
 
        else:
            print("Solving at runtime failed")
            # Can't do anything, really
            pass

    # Fall back to default.
    return code

def optimize(code: language.Commands):
    """Take program as an input and return optimized program instance (resolve
    simple loops, trivial expressions, trivial conditions etc."""
    manager = parse.IDENTIFIERS_MANAGER

    # Optimizer will try to trivialize/optimize as long as anything changes.
    proceed = True
    while proceed:
        proceed = False
        # Remove variables and arrays that are never used in code.
        if remove_unused_variables(code, manager):
            proceed = True

        if remove_unused_arrays(code, manager):
            proceed = True

        ##print("BEFORE:")
        #code.#print_out()
        # Remove values that are only assigned to, but never actually used.
        if remove_only_assigns(code, manager):
            proceed = True
        ##print("AFTER:")
        #code.#print_out()

        # Try to wrap variables so they can be substituted with constants.
        if wrap_variables(code, manager):
            proceed = True

        if wrap_array_cells(code, manager):
            proceed = True

        code = trivial_optimizer.optimize(code)

        # Set some values to register only mode. GO SONIC GO!!!

    #    all_stuff = code.get_all_containing(manager.variables["f"])
        #parse.IDENTIFIERS_MANAGER = manager

        ##print("AFTER OPTIMALISATIONS: ")

#    turbo_variables(code, manager)
    #print()
    #print()
    #print()

    #code.print_out()

    result = life_span(code, manager)
    if not result:
        turbo_variables(code, manager)

    #print()
    #print()
    code = solve_at_compile_time(code, manager, 30)

    ##print(DG.nodes())

    # TODO: last step of optimization is trying to interpret program and return
    # only results. Give it timeout of 3 minutes.
    return code


def life_span(code: language.Commands, manager: parse.IdentifiersManager):
    # WORK ONLY ON COMPLETELY FLAT STRUCTURES:
    for command in code.get_ordered_list():
        if len(code.get_path_to(command)) > 2:
            #print("SKIPPING DYNAMIC ALLOCATION DUE TO NON FLAT STRUCTURE")
            return False

    # Find first and last object of life span..
    manager.life_span_variables = {}
    for key in manager.variables:
        val = manager.variables[key]
        using = code.get_all_containing(val)
        if len(using) > 1:
            try:
                using[0].life_start.append(key)
            except AttributeError:
                using[0].life_start = [key]

            try:
                using[-1].life_end.append(key)
            except AttributeError:
                using[-1].life_end = [key]
            manager.life_span_variables[key] = (using[0], using[-1])

    # Find all objects in life span.
    for key in manager.life_span_variables:
        objects_used = []
        pair = manager.life_span_variables[key]
        first = pair[0]
        second = pair[1]
        counter = 0
        calculate = False
        for command in code.get_ordered_list():
            if command is first:
                calculate = True

            if calculate:
                counter += 1
                objects_used.append(command)
            if command is second:
                break
        manager.life_span_variables[key] = (first, second, objects_used, counter)

    # Find variable pairs, that can be used in registers independently.
    # Set all to False.
    pairs_independent = {}
    for first in manager.life_span_variables:
        for second in manager.life_span_variables:
            pairs_independent[(first, second)] = False

    # Calculate which are True.
    for key in manager.life_span_variables:
        stuff = manager.life_span_variables[key]
        first = stuff[0]
        last = stuff[1]
        objects_used = stuff[2]
        counter = stuff[3]
        for second_key in manager.life_span_variables:
            if key is second_key:
                continue
            second_stuff = manager.life_span_variables[second_key]
            second_first = second_stuff[0]
            second_last = second_stuff[1]
            second_objects_used = second_stuff[2]
            second_counter = second_stuff[3]

            independent = True
            for first_object in objects_used:
                for second_object in second_objects_used:
                    if first_object is second_object:
                        independent = False
                        break
            if independent:
                pairs_independent[(key, second_key)] = True

    #for command in code.get_ordered_list():
        #path = code.get_path_to(command)
        #for key in manager.life_span_variables:
            #if command in manager.life_span_variables[key][2]:
                #print(key, end=" ")
            #else:
                #print(" " * len(key), end=" ")

        #print(" " * len(path) * 4 + str(command))

    #print(manager.life_span_variables)

    # Filter out only those independent.
    result = {}
    for pair in pairs_independent:
        if pairs_independent[pair]:
            result[pair] = True
    pairs_independent = result

    # Print this stuff out.

    #for pair in pairs_independent:
        #print(str(pair) + " " + str(pairs_independent[pair]))

    # Find best possible variables to go reg only.
    to_convert = []
    for pair in pairs_independent:
        for val in pair:
            add = True
            for already in to_convert:
                if not ((already, val) in pairs_independent):
                    add = False
            if add:
                to_convert.append(val)

    # Print this better stuff out.
    #print("REG ONLY: ")
    #print(to_convert)

    # GIVE THAT TURBO TO THEM!!!
    for key in to_convert:
        stuff = manager.life_span_variables[key]
        first = stuff[0]
        last = stuff[1]
        # Insert GO REG ONLY before first and DELETE REGISTER after last.
        # Get last parent of first.
        parent: language.Commands = code.get_path_to(first)[-2]
        # Get index of first.
        index = parent.commands.index(first)
        parent.add_command_at_position(optimizer_stuff.VariableToRegisterStart(manager.variables[key]), index)

        # Get last parent of last.
        parent: language.Commands = code.get_path_to(last)[-2]
        # Get index of last.
        index = parent.commands.index(last)
        parent.add_command_at_position(optimizer_stuff.DeleteRegister(manager.variables[key]),
                                       index+1)

    if to_convert:
        return True

    return False



def decompose_expression(expression: language.Expression):
    if isinstance(expression, language.ExpressionSingle):
        return [expression.value]
    elif isinstance(expression, language.ExpressionOperation):
        return [expression.first, expression.second]


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        #print("Usage: optimizer.py file_name")
        sys.exit(1)

    program = parse.get_code(sys.argv[1])
    program.print_out()
    #print("AFTER")
    optimize(program)
    program.print_out()
