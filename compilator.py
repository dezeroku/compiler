import argparse

import parse

import language

import trivial_optimizer

import optimizer

import better_compiler as compiler_mod

import best_compiler


class CompilationManager:
    def __init__(self, compiler, trivial_optimizer=False, optimizer=False):
        self.compiler = compiler
        self.trivial_optimizer = trivial_optimizer
        self.optimizer = optimizer

    def compile(self, program: language.Program, identifiers):
        if self.trivial_optimizer:
            program.block = self.trivial_optimizer(program.block)
        if self.optimizer:
            program.block = self.optimizer(program.block)

        compiler = self.compiler(program, identifiers)
        return compiler.compile()


def main():
    parser = argparse.ArgumentParser("Let's compile some code!")

    parser.add_argument("input_file", help="Input file name (source code).")
    parser.add_argument("output_file", help="Output file name (machine code).")
    parser.add_argument("--debug", "-d", help="Turn on debugging comments in\
                        output code.", action="store_true")
    parser.add_argument("--no-optimalization", help="Disable additional\
                        optimalisations.",
                        action="store_false")
    parser.add_argument("-O3", help="Just try it baby!", action="store_true")

    args = parser.parse_args()

    compiler = compiler_mod.Compiler
    trivial_optimizer_obj = False
    optimizer_obj = False

    if args.debug:
        compiler_mod.DEBUG = True
        best_compiler.DEBUG = True
        optimizer.DEBUG = True

    code = parse.get_code(args.input_file)

    if args.no_optimalization:
        trivial_optimizer_obj = trivial_optimizer.optimize

    if args.O3:
        optimizer_obj = optimizer.optimize
        compiler = best_compiler.Compiler

    manager = CompilationManager(compiler, trivial_optimizer_obj,
                                 optimizer_obj)

    result = manager.compile(code, parse.IDENTIFIERS_MANAGER)

    with open(args.output_file, "w") as output:
        output.write(result)


if __name__ == "__main__":
    main()
