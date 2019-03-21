import tempfile
import subprocess

import pytest
#pytestmark = pytest.mark.skip("all tests green")

# TODO: parse has some globals that have to be reset to work properly.
import parse
from basic_compiler import Compiler

def run_code_and_get_results(code: str):
    program = parse.get_code_from_string(code)

    compiler = Compiler(program, parse.IDENTIFIERS_MANAGER)

    try:
        machine_code = compiler.compile()
        parse.reset()
    except:
        parse.reset()

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


@pytest.mark.skip
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


@pytest.mark.skip
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
