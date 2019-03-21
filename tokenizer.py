import sys

import ply.lex as lex

tokens = ('DECLARE', 'IN', 'END', 'IF', 'THEN', 'ELSE', 'ENDIF', 'WHILE', 'DO',
         'ENDWHILE', 'ENDDO', 'FOR', 'FROM', 'TO', 'ENDFOR', 'DOWNTO', 'READ',
         'WRITE', 'pidentifier', 'NUMBER', 'COMMENT_START', 'COMMENT_END',
          'ASSIGN', 'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'MODULO', 'EQUALS',
         'NOT_EQUALS', 'LOWER_THEN', 'GREATER_THEN', 'LOWER_EQUAL',
          'GREATER_EQUAL', 'COLON', 'SEMICOLON', 'LPAREN', 'RPAREN', 'NEWLINE')

t_ignore = '\t\r '


def t_NEWLINE(t):
    r'\n'
    t.lexer.lineno += 1


def t_error(t):
    if t.lexer.comment is True:
        t.lexer.skip(1)
        return
    else:
        print("Unrecognized character:" + str(t.value))
        print("At line: " + str(t.lexer.lineno))
        sys.exit(1)


def t_DECLARE(t):
    r'DECLARE'
    if not t.lexer.comment:
        return t


def t_IN(t):
    r'IN'
    if not t.lexer.comment:
        return t


def t_IF(t):
    r'IF'
    if not t.lexer.comment:
        return t


def t_THEN(t):
    r'THEN'
    if not t.lexer.comment:
        return t


def t_ELSE(t):
    r'ELSE'
    if not t.lexer.comment:
        return t


def t_ENDIF(t):
    r'ENDIF'
    if not t.lexer.comment:
        return t


def t_WHILE(t):
    r'WHILE'
    if not t.lexer.comment:
        return t


def t_DOWNTO(t):
    r'DOWNTO'
    if not t.lexer.comment:
        return t

def t_DO(t):
    r'DO'
    if not t.lexer.comment:
        return t


def t_ENDWHILE(t):
    r'ENDWHILE'
    if not t.lexer.comment:
        return t


def t_ENDDO(t):
    r'ENDDO'
    if not t.lexer.comment:
        return t


def t_FOR(t):
    r'FOR'
    if not t.lexer.comment:
        return t


def t_FROM(t):
    r'FROM'
    if not t.lexer.comment:
        return t


def t_TO(t):
    r'TO'
    if not t.lexer.comment:
        return t


def t_ENDFOR(t):
    r'ENDFOR'
    if not t.lexer.comment:
        return t


def t_READ(t):
    r'READ'
    if not t.lexer.comment:
        return t


def t_WRITE(t):
    r'WRITE'
    if not t.lexer.comment:
        return t


def t_ASSIGN(t):
    r':='
    if not t.lexer.comment:
        return t


def t_PLUS(t):
    r'\+'
    if not t.lexer.comment:
        return t


def t_MINUS(t):
    r'\-'
    if not t.lexer.comment:
        return t


def t_MULTIPLY(t):
    r'\*'
    if not t.lexer.comment:
        return t


def t_DIVIDE(t):
    r'\/'
    if not t.lexer.comment:
        return t


def t_MODULO(t):
    r'\%'
    if not t.lexer.comment:
        return t


def t_NOT_EQUALS(t):
    r'!='
    if not t.lexer.comment:
        return t


def t_LOWER_EQUAL(t):
    r'<='
    if not t.lexer.comment:
        return t


def t_GREATER_EQUAL(t):
    r'>='
    if not t.lexer.comment:
        return t


def t_EQUALS(t):
    r'='
    if not t.lexer.comment:
        return t


def t_LOWER_THEN(t):
    r'<'
    if not t.lexer.comment:
        return t


def t_GREATER_THEN(t):
    r'>'
    if not t.lexer.comment:
        return t


def t_COLON(t):
    r':'
    if not t.lexer.comment:
        return t


def t_SEMICOLON(t):
    r';'
    if not t.lexer.comment:
        return t


def t_LPAREN(t):
    r'\('
    if not t.lexer.comment:
        return t


def t_RPAREN(t):
    r'\)'
    if not t.lexer.comment:
        return t


def t_pidentifier(t):
    r'[_a-z]+'
    if not t.lexer.comment:
        return t


def t_NUMBER(t):
    r'[0-9]+'
    if not t.lexer.comment:
        return t


def t_COMMENT_START(t):
    r'\['
    t.lexer.comment = True


def t_COMMENT_END(t):
    r'\]'
    t.lexer.comment = False


def t_END(t):
    r'END'
    if not t.lexer.comment:
        return t



def get_lexer():
    lexer = lex.lex()
    lexer.comment = False

    return lexer


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: tokenize.py filename")

    with open(sys.argv[1], "r") as codefile:
        content = codefile.read()

    lexer = get_lexer()
    lexer.input(content)

    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)
