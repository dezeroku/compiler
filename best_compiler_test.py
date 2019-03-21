import tempfile
import subprocess

import pytest

# TODO: parse has some globals that have to be reset to work properly.
import parse

import trivial_optimizer
import optimizer

from best_compiler import Compiler
import best_compiler

from compilator import CompilationManager

def run_code_and_get_results(code: str):
    program = parse.get_code_from_string(code)

    compiler = CompilationManager(Compiler, trivial_optimizer.optimize,
                                  optimizer.optimize)
    best_compiler.INDENTATION = 0

    try:
        machine_code = compiler.compile(program, parse.IDENTIFIERS_MANAGER)
        parse.reset()
    except:
        parse.reset()
        return

    with open(".test_file_compile", "w") as test_file:
        test_file.write(machine_code)
    result = subprocess.run(["./maszyna_rejestrowa/maszyna-rejestrowa",
                             ".test_file_compile"],
                            capture_output=True)
    result = result.stdout.decode("utf-8")
    result = result.split("\n")
    result = result[3:-2]
    result = list(map(lambda x: x[2:], result))
    return result


def run_code_and_get_results_with_input(code: str, input_string: str):
    program = parse.get_code_from_string(code)

    compiler = CompilationManager(Compiler, trivial_optimizer.optimize,
                                  optimizer.optimize)
    best_compiler.INDENTATION = 0

    try:
        machine_code = compiler.compile(program, parse.IDENTIFIERS_MANAGER)
        parse.reset()
    except:
        parse.reset()
        return

    with open(".test_file_compile", "w") as test_file:
        test_file.write(machine_code)
    result = subprocess.run(["./maszyna_rejestrowa/maszyna-rejestrowa",
                             ".test_file_compile"],
                            capture_output=True,
                            input=input_string.encode("utf-8"))
    result = result.stdout.decode("utf-8")
    result = result.split("\n")
    result = result[3:-2]
    result = list(map(lambda x: x[2:], result))
    result[0] = result[0][2:]
    return result


def test_basic_assign():
    code = """
DECLARE
 a;
IN
  a := 2;
  WRITE a;
END"""
    result = run_code_and_get_results(code)
    print(result)
    assert result[0] == "2"


def test_assign_variable():
    code = """
DECLARE
 a; b;
IN
  a := 2;
  b := a;
  WRITE a;
  WRITE b;
END"""
    result = run_code_and_get_results(code)
    print(result)
    assert result[0] == "2"
    assert result[1] == "2"


def test_assign_number_plus_number():
    code = """
DECLARE
 a;
IN
  a := 2 + 2;
  WRITE a;
END"""
    result = run_code_and_get_results(code)
    print(result)
    assert result[0] == "4"


def test_assign_number_plus_variable():
    code = """
DECLARE
 a; b;
IN
  a := 2;
  b := 2 + a;
  WRITE b;
END"""
    result = run_code_and_get_results(code)
    print(result)
    assert result[0] == "4"


def test_assign_number_minus_variable():
    code = """
DECLARE
 a; b;
IN
  a := 1;
  b := 2 - a;
  WRITE b;
END"""
    result = run_code_and_get_results(code)
    print(result)
    assert result[0] == "1"


def test_assign_number_multiply_variable():
    code = """
DECLARE
 a; b;
IN
  a := 2;
  b := 2 * a;
  WRITE b;
END"""
    result = run_code_and_get_results(code)
    print(result)
    assert result[0] == "4"


def test_condition_if_equals():
    code = """
DECLARE
 a; b;
IN
  a := 1;
  b := 2;
  IF a = 1 THEN
  WRITE a;
  ENDIF
END"""
    result = run_code_and_get_results(code)
    print(result)
    assert len(result) == 1
    assert result[0] == "1"

def test_condition_if_equals_two():
    code = """
DECLARE
 a; b;
IN
  a := 1;
  b := 2;
  IF a = 2 THEN
  WRITE a;
  ENDIF
END"""
    result = run_code_and_get_results(code)
    print(result)
    assert len(result) == 0


def test_condition_if_not_equals():
    code = """
DECLARE
 a; b;
IN
  a := 1;
  b := 2;
  IF a != 1 THEN
  WRITE a;
  ENDIF
END"""
    result = run_code_and_get_results(code)
    print(result)
    assert len(result) == 0

def test_condition_if_not_equals_two():
    code = """
DECLARE
 a; b;
IN
  a := 1;
  b := 2;
  IF a != 2 THEN
  WRITE a;
  ENDIF
END"""
    result = run_code_and_get_results(code)
    print(result)
    assert len(result) == 1
    assert result[0] == "1"


def test_condition_if_smaller_equals():
    code = """
DECLARE
 a; b;
IN
  a := 1;
  b := 2;
  IF a <= 1 THEN
  WRITE a;
  ENDIF
END"""
    result = run_code_and_get_results(code)
    print(result)
    assert len(result) == 1
    assert result[0] == "1"

def test_condition_if_smaller_equals_two():
    code = """
DECLARE
 a; b;
IN
  a := 2;
  b := 2;
  IF a <= 1 THEN
  WRITE a;
  ENDIF
END"""
    result = run_code_and_get_results(code)
    print(result)
    assert len(result) == 0

def test_condition_if_bigger_equals():
    code = """
DECLARE
 a; b;
IN
  a := 1;
  b := 2;
  IF a >= 1 THEN
  WRITE a;
  ENDIF
END"""
    result = run_code_and_get_results(code)
    print(result)
    assert len(result) == 1
    assert result[0] == "1"

def test_condition_if_bigger_equals_two():
    code = """
DECLARE
 a; b;
IN
  a := 1;
  b := 2;
  IF a >= 2 THEN
  WRITE a;
  ENDIF
END"""
    result = run_code_and_get_results(code)
    print(result)
    assert len(result) == 0

def test_condition_if_bigger_equals_three():
    code = """
DECLARE
 a; b;
IN
  a := 1;
  b := 2;
  IF a >= 0 THEN
  WRITE a;
  ENDIF
END"""
    result = run_code_and_get_results(code)
    print(result)
    assert len(result) == 1
    assert result[0] == "1"


def test_condition_if_smaller():
    code = """
DECLARE
 a; b;
IN
  a := 1;
  b := 2;
  IF a < 2 THEN
  WRITE a;
  ENDIF
END"""
    result = run_code_and_get_results(code)
    print(result)
    assert len(result) == 1
    assert result[0] == "1"


def test_condition_if_smaller_two():
    code = """
DECLARE
 a; b;
IN
  a := 2;
  b := 2;
  IF a < 1 THEN
  WRITE a;
  ENDIF
END"""
    result = run_code_and_get_results(code)
    print(result)
    assert len(result) == 0


def test_condition_if_bigger():
    code = """
DECLARE
 a; b;
IN
  a := 1;
  b := 2;
  IF a > 0 THEN
  WRITE a;
  ENDIF
END"""
    result = run_code_and_get_results(code)
    print(result)
    assert len(result) == 1
    assert result[0] == "1"


def test_condition_if_bigger_two():
    code = """
DECLARE
 a; b;
IN
  a := 1;
  b := 2;
  IF a > 2 THEN
  WRITE a;
  ENDIF
END"""
    result = run_code_and_get_results(code)
    print(result)
    assert len(result) == 0


def test_condition_if_else_equals():
    code = """
DECLARE
 a; b;
IN
  a := 1;
  b := 2;
  IF a = 1 THEN
  WRITE a;
  ELSE
  WRITE b;
  ENDIF
END"""
    result = run_code_and_get_results(code)
    print(result)
    assert len(result) == 1
    assert result[0] == "1"


def test_condition_if_else_not_equals():
    code = """
DECLARE
 a; b;
IN
  a := 1;
  b := 2;
  IF a != 1 THEN
  WRITE a;
  ELSE
  WRITE b;
  ENDIF
END"""
    result = run_code_and_get_results(code)
    print(result)
    assert len(result) == 1
    assert result[0] == "2"


def test_while_bigger_equals():
    code ="""
DECLARE
  a;
IN
  a := 10;

  WHILE a >= 5 DO
    WRITE a;
    a := a - 1;
  ENDWHILE
END
    """
    result = run_code_and_get_results(code)
    print(result)
    assert result[0] == "10"
    assert result[1] == "9"
    assert result[2] == "8"
    assert result[3] == "7"
    assert result[4] == "6"
    assert result[5] == "5"
    assert len(result) == 6


def test_while_bigger():
    code ="""
DECLARE
  a;
IN
  a := 10;

  WHILE a > 5 DO
    WRITE a;
    a := a - 1;
  ENDWHILE
END
    """
    result = run_code_and_get_results(code)
    print(result)
    assert result[0] == "10"
    assert result[1] == "9"
    assert result[2] == "8"
    assert result[3] == "7"
    assert result[4] == "6"
    assert len(result) == 5



def test_while_lower_equals():
    code ="""
DECLARE
  a;
IN
  a := 5;

  WHILE a <= 10 DO
    WRITE a;
    a := a + 1;
  ENDWHILE
END
    """
    result = run_code_and_get_results(code)
    print(result)
    assert result[0] == "5"
    assert result[1] == "6"
    assert result[2] == "7"
    assert result[3] == "8"
    assert result[4] == "9"
    assert result[5] == "10"
    assert len(result) == 6


def test_while_lower():
    code ="""
DECLARE
  a;
IN
  a := 5;

  WHILE a < 10 DO
    WRITE a;
    a := a + 1;
  ENDWHILE
END
    """
    result = run_code_and_get_results(code)
    print(result)
    assert result[0] == "5"
    assert result[1] == "6"
    assert result[2] == "7"
    assert result[3] == "8"
    assert result[4] == "9"
    assert len(result) == 5

def test_while_lower_variable():
    code ="""
DECLARE
  a; b;
IN
  a := 5;
  b := 10;

  WHILE a < b DO
    WRITE a;
    a := a + 1;
  ENDWHILE
END
    """
    result = run_code_and_get_results(code)
    print(result)
    assert result[0] == "5"
    assert result[1] == "6"
    assert result[2] == "7"
    assert result[3] == "8"
    assert result[4] == "9"
    assert len(result) == 5

def test_while_lower_equals_variable():
    code ="""
DECLARE
  a; b;
IN
  a := 5;
  b := 10;

  WHILE a <= b DO
    WRITE a;
    a := a + 1;
  ENDWHILE
END
    """
    result = run_code_and_get_results(code)
    print(result)
    assert result[0] == "5"
    assert result[1] == "6"
    assert result[2] == "7"
    assert result[3] == "8"
    assert result[4] == "9"
    assert result[5] == "10"
    assert len(result) == 6

def test_while_bigger_variable():
    code ="""
DECLARE
  a; b;
IN
  a := 10;
  b := 5;

  WHILE a > b DO
    WRITE a;
    a := a - 1;
  ENDWHILE
END
    """
    result = run_code_and_get_results(code)
    print(result)
    assert result[0] == "10"
    assert result[1] == "9"
    assert result[2] == "8"
    assert result[3] == "7"
    assert result[4] == "6"
    assert len(result) == 5


def test_while_bigger_equals_variable():
    code ="""
DECLARE
  a; b;
IN
  a := 10;
  b := 5;

  WHILE a >= b DO
    WRITE a;
    a := a - 1;
  ENDWHILE
END
    """
    result = run_code_and_get_results(code)
    print(result)
    assert result[0] == "10"
    assert result[1] == "9"
    assert result[2] == "8"
    assert result[3] == "7"
    assert result[4] == "6"
    assert result[5] == "5"
    assert len(result) == 6


def test_multiplication_by_zero():
    code = """
DECLARE
    a; 
IN
  a := 7;
  a := a * 0;
  WRITE a;
END
    """
    result = run_code_and_get_results(code)
    assert len(result) == 1
    assert result[0] == "0"


def test_multiplication_by_zero_two():
    code = """
DECLARE
    a; 
IN
  a := 7;
  a := 0 * 7;
  WRITE a;
END
    """
    result = run_code_and_get_results(code)
    assert len(result) == 1
    assert result[0] == "0"


def test_multiplication_by_zero_variable():
    code = """
DECLARE
    a; b;
IN
  a := 7;
  b := 0;
  a := a * b;
  WRITE a;
END
    """
    result = run_code_and_get_results(code)
    assert len(result) == 1
    assert result[0] == "0"


def test_multiplication_by_zero_variable_two():
    code = """
DECLARE
    a; b;
IN
  a := 7;
  b := 0;
  a := b * a;
  WRITE a;
END
    """
    result = run_code_and_get_results(code)
    assert len(result) == 1
    assert result[0] == "0"

def test_division_no_rest():
    code = """
DECLARE
    a;
IN
  a := 4;
  a := a / 4;
  WRITE a;
END
    """
    result = run_code_and_get_results(code)
    assert len(result) == 1
    assert result[0] == "1"


def test_division_rest():
    code = """
DECLARE
    a;
IN
  a := 7;
  a := a / 4;
  WRITE a;
END
    """
    result = run_code_and_get_results(code)
    assert len(result) == 1
    assert result[0] == "1"


def test_division_no_rest_variable():
    code = """
DECLARE
    a; b;
IN
  a := 4;
  b := 4;
  a := a / b;
  WRITE a;
END
    """
    result = run_code_and_get_results(code)
    assert len(result) == 1
    assert result[0] == "1"


def test_division_rest_variable():
    code = """
DECLARE
    a; b;
IN
  a := 7;
  b := 4;
  a := a / b;
  WRITE a;
END
    """
    result = run_code_and_get_results(code)
    assert len(result) == 1
    assert result[0] == "1"


def test_division_by_zero():
    code = """
DECLARE
    a; 
IN
  a := 7;
  a := a / 0;
  WRITE a;
END
    """
    result = run_code_and_get_results(code)
    assert len(result) == 1
    assert result[0] == "0"


def test_division_by_zero_variable():
    code = """
DECLARE
    a; b;
IN
  a := 7;
  b := 0;
  a := a / b;
  WRITE a;
END
    """
    result = run_code_and_get_results(code)
    assert len(result) == 1
    assert result[0] == "0"


def test_division_zero():
    code = """
DECLARE
    a; 
IN
  a := 0 / 7;
  WRITE a;
END
    """
    result = run_code_and_get_results(code)
    assert len(result) == 1
    assert result[0] == "0"


def test_division_zero_variable():
    code = """
DECLARE
    a; b;
IN
  a := 7;
  b := 0;
  a := b / a;
  WRITE a;
END
    """
    result = run_code_and_get_results(code)
    assert len(result) == 1
    assert result[0] == "0"


def test_modulo():
    code = """
DECLARE
    a;
IN
    a := 5 % 2;
    WRITE a;
END"""
    result = run_code_and_get_results(code)
    assert len(result) == 1
    assert result[0] == "1"


def test_modulo_variable():
    code = """
DECLARE
    a; b;
IN
    b := 2;
    a := 5 % b;
    WRITE a;
END"""
    result = run_code_and_get_results(code)
    assert len(result) == 1
    assert result[0] == "1"


def test_modulo_no_rest():
    code = """
DECLARE
    a;
IN
    a := 4 % 2;
    WRITE a;
END"""
    result = run_code_and_get_results(code)
    assert len(result) == 1
    assert result[0] == "0"


def test_modulo_no_rest_variable():
    code = """
DECLARE
    a; b;
IN
    b := 2;
    a := 4 % b;
    WRITE a;
END"""
    result = run_code_and_get_results(code)
    assert len(result) == 1
    assert result[0] == "0"


def test_modulo_by_zero():
    code = """
DECLARE
    a;
IN
    a := 4 % 0;
    WRITE a;
END"""
    result = run_code_and_get_results(code)
    assert len(result) == 1
    assert result[0] == "0"


def test_modulo_by_zero_variable():
    code = """
DECLARE
    a; b;
IN
    b := 0;
    a := 4 % b;
    WRITE a;
END"""
    result = run_code_and_get_results(code)
    assert len(result) == 1
    assert result[0] == "0"


def test_modulo_zero():
    code = """
DECLARE
    a;
IN
    a := 0 % 4;
    WRITE a;
END"""
    result = run_code_and_get_results(code)
    assert len(result) == 1
    assert result[0] == "0"


def test_modulo_zero_variable():
    code = """
DECLARE
    a;
IN
    a := 0;
    a := a % 4;
    WRITE a;
END"""
    result = run_code_and_get_results(code)
    assert len(result) == 1
    assert result[0] == "0"


def test_do_while():
    code = """
DECLARE
    a;
IN
    a := 1;
    DO
        WRITE a;
    WHILE a > 10
    ENDDO
END"""
    result = run_code_and_get_results(code)
    assert len(result) == 1
    assert result[0] == "1"


def test_do_while_normal():
    code = """
DECLARE
    a;
IN
    a := 1;
    DO
        WRITE a;
        a := a + 1;
    WHILE a < 5
    ENDDO
END"""
    result = run_code_and_get_results(code)
    assert len(result) == 4
    assert result[0] == "1"
    assert result[1] == "2"
    assert result[2] == "3"
    assert result[3] == "4"


def test_array_cell():
    code = """
DECLARE
a(10:100);
IN
    a(10) := 4;
    WRITE a(10);
END
    """
    result = run_code_and_get_results(code)
    assert len(result) == 1
    assert result[0] == "4"


def test_array_cell_variable():
    code = """
DECLARE
a(10:100); b;
IN
    b := 10;
    a(b) := 4;
    WRITE a(b);
END
    """
    result = run_code_and_get_results(code)
    assert len(result) == 1
    assert result[0] == "4"


def test_for():
    code = """
DECLARE
IN
    FOR i FROM 2 TO 5 DO
        WRITE i;
    ENDFOR
END
    """
    result = run_code_and_get_results(code)
    assert len(result) == 4
    assert result[0] == '2'
    assert result[1] == '3'
    assert result[2] == '4'
    assert result[3] == '5'


def test_for_variable():
    code = """
DECLARE
    a;
IN
    a := 5;
    FOR i FROM 2 TO a DO
        WRITE i;
    ENDFOR
END
    """
    result = run_code_and_get_results(code)
    assert len(result) == 4
    assert result[0] == '2'
    assert result[1] == '3'
    assert result[2] == '4'
    assert result[3] == '5'


def test_for_variable_changed():
    code = """
DECLARE
    a;
IN
    a := 5;
    FOR i FROM 2 TO a DO
        a := a + i;
        WRITE i;
    ENDFOR
END
    """
    result = run_code_and_get_results(code)
    assert len(result) == 4
    assert result[0] == '2'
    assert result[1] == '3'
    assert result[2] == '4'
    assert result[3] == '5'


def test_for_loop_variable_iterator_array_cells():
    code = """
DECLARE
    a; b(2:5);
IN
    a := 5;
    FOR i FROM 2 TO a DO
        b(i) := a + i;
        WRITE b(i);
    ENDFOR
END
    """
    result = run_code_and_get_results(code)
    assert len(result) == 4
    assert result[0] == '7'
    assert result[1] == '8'
    assert result[2] == '9'
    assert result[3] == '10'


def test_for_backwards():
    code = """
DECLARE
IN
    FOR i FROM 5 DOWNTO 2 DO
        WRITE i;
    ENDFOR
END
    """
    result = run_code_and_get_results(code)
    assert len(result) == 4
    assert result[0] == '5'
    assert result[1] == '4'
    assert result[2] == '3'
    assert result[3] == '2'


def test_for_backwards_variable():
    code = """
DECLARE
    a;
IN
    a := 5;
    FOR i FROM a DOWNTO 2 DO
        WRITE i;
    ENDFOR
END
    """
    result = run_code_and_get_results(code)
    assert len(result) == 4
    assert result[0] == '5'
    assert result[1] == '4'
    assert result[2] == '3'
    assert result[3] == '2'


def test_for_backwards_variable_changed():
    code = """
DECLARE
    a;
IN
    a := 5;
    FOR i FROM a DOWNTO 2 DO
        a := a + i;
        WRITE i;
    ENDFOR
END
    """
    result = run_code_and_get_results(code)
    assert len(result) == 4
    assert result[0] == '5'
    assert result[1] == '4'
    assert result[2] == '3'
    assert result[3] == '2'


def test_for_backwards_loop_variable_iterator_array_cells():
    code = """
DECLARE
    a; b(2:5);
IN
    a := 5;
    FOR i FROM a DOWNTO 2 DO
        b(i) := a + i;
        WRITE b(i);
    ENDFOR
END
    """
    result = run_code_and_get_results(code)
    assert len(result) == 4
    assert result[0] == '10'
    assert result[1] == '9'
    assert result[2] == '8'
    assert result[3] == '7'


def test_for_empty():
    code = """
DECLARE
    a; b(2:5);
IN
    a := 7;
    FOR i FROM a TO 6 DO
        b(i) := a + i;
        WRITE b(i);
    ENDFOR
END
    """
    result = run_code_and_get_results(code)
    assert len(result) == 0


def test_for_backwards_empty():
    code = """
DECLARE
    a; b(2:5);
IN
    a := 5;
    FOR i FROM a DOWNTO 6 DO
        b(i) := a + i;
        WRITE b(i);
    ENDFOR
END
    """
    result = run_code_and_get_results(code)
    assert len(result) == 0


def test_loop_identifier_different_name():
    code = """
DECLARE
    sito(2:100); a;
IN
    a := 123;

    FOR i FROM 5 DOWNTO 2 DO
        sito(i) := 1;
    ENDFOR
    FOR j FROM 5 DOWNTO 2 DO
        WRITE sito(j);
    ENDFOR
END
    """
    result = run_code_and_get_results(code)
    assert len(result) == 4
    assert result[0] == "1"
    assert result[1] == "1"
    assert result[2] == "1"
    assert result[3] == "1"


def test_loop_identifier_same_name():
    code = """
DECLARE
    sito(2:5); a;
IN
    a := 123;

    FOR i FROM 5 DOWNTO 2 DO
        sito(i) := 1;
    ENDFOR

    FOR i FROM 5 DOWNTO 2 DO
        WRITE sito(i);
    ENDFOR
END
    """
    result = run_code_and_get_results(code)
    assert len(result) == 4
    assert result[0] == "1"
    assert result[1] == "1"
    assert result[2] == "1"
    assert result[3] == "1"


def test_ertostenes():
    code = """
[ sito Eratostenesa ]
DECLARE
    n; j; sito(2:100);
IN
    n := 100;
    FOR i FROM n DOWNTO 2 DO
        sito(i) := 1;
    ENDFOR
    FOR i FROM 2 TO n DO
        IF sito(i) != 0 THEN
            j := i + i;
            WHILE j <= n DO
                sito(j) := 0;
                j := j + i;
            ENDWHILE
            WRITE i;
        ENDIF
    ENDFOR
END
    """
    result = run_code_and_get_results(code)
    assert len(result) == 25
    assert result[0] == "2"
    assert result[1] == "3"
    assert result[2] == "5"
    assert result[3] == "7"
    assert result[4] == "11"
    assert result[5] == "13"
    assert result[6] == "17"
    assert result[7] == "19"
    assert result[8] == "23"
    assert result[9] == "29"
    assert result[10] == "31"
    assert result[11] == "37"
    assert result[12] == "41"
    assert result[13] == "43"
    assert result[14] == "47"
    assert result[15] == "53"
    assert result[16] == "59"
    assert result[17] == "61"
    assert result[18] == "67"
    assert result[19] == "71"
    assert result[20] == "73"
    assert result[21] == "79"
    assert result[22] == "83"
    assert result[23] == "89"
    assert result[24] == "97"


def test_program0():
    code = """
DECLARE
    a; b;
IN
    READ a;
    WHILE a>0 DO
        b:=a/2;
        b:=2*b;
        IF a>b THEN 
            WRITE 1;
        ELSE 
            WRITE 0;
        ENDIF
        a:=a/2;
    ENDWHILE
END"""
    result = run_code_and_get_results_with_input(code, "1345601\n")
    assert len(result) == 21
    result = "".join(result)
    assert result == "100000100001000100101"


def test_program2_1():
    code="""[ Rozklad liczby na czynniki pierwsze ]
DECLARE
    n; m; reszta; potega; dzielnik;
IN
    READ n;
    dzielnik := 2;
    m := dzielnik * dzielnik;
    WHILE n >= m DO
        potega := 0;
        reszta := n % dzielnik;
        WHILE reszta = 0 DO
            n := n / dzielnik;
            potega := potega + 1;
            reszta := n % dzielnik;
        ENDWHILE
        IF potega > 0 THEN [ czy znaleziono dzielnik ]
            WRITE dzielnik;
            WRITE potega;
        ELSE
            dzielnik := dzielnik + 1;
            m := dzielnik * dzielnik;
        ENDIF
    ENDWHILE
    IF n != 1 THEN [ ostatni dzielnik ]
        WRITE n;
        WRITE 1;
    ENDIF
END"""
    result = run_code_and_get_results_with_input(code, "12345678901\n")
    assert len(result) == 4
    assert result[0] == "857"
    assert result[1] == "1"
    assert result[2] == "14405693"
    assert result[3] == "1"

def test_program2_2():
    code="""[ Rozklad liczby na czynniki pierwsze ]
DECLARE
    n; m; reszta; potega; dzielnik;
IN
    READ n;
    dzielnik := 2;
    m := dzielnik * dzielnik;
    WHILE n >= m DO
        potega := 0;
        reszta := n % dzielnik;
        WHILE reszta = 0 DO
            n := n / dzielnik;
            potega := potega + 1;
            reszta := n % dzielnik;
        ENDWHILE
        IF potega > 0 THEN [ czy znaleziono dzielnik ]
            WRITE dzielnik;
            WRITE potega;
        ELSE
            dzielnik := dzielnik + 1;
            m := dzielnik * dzielnik;
        ENDIF
    ENDWHILE
    IF n != 1 THEN [ ostatni dzielnik ]
        WRITE n;
        WRITE 1;
    ENDIF
END"""
    result = run_code_and_get_results_with_input(code, "12345678903\n")
    assert len(result) == 4
    assert result[0] == "3"
    assert result[1] == "1"
    assert result[2] == "4115226301"
    assert result[3] == "1"
