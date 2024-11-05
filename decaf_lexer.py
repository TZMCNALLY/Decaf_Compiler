import sys

# Names for each token in Decaf
tokens = ('LEFT_CB',
          'RIGHT_CB',
          'LEFT_SQB',
          'RIGHT_SQB',
          'LEFT_PN',
          'RIGHT_PN',
          'SEMI_COLON',
          'COMMA',
          'DOT',
          'PLUS',
          'MINUS',
          'STAR',
          'F_SLASH',
          'ASSIGN',
          'INCREMENT',
          'DECREMENT',
          'AND',
          'OR',
          'NOT',
          'EQ',
          'NOT_EQ',
          'LT',
          'LTE',
          'GT',
          'GTE',
          'CLASS',
          'EXTENDS',
          'PUBLIC',
          'PRIVATE',
          'STATIC',
          'TYPE_INT',
          'TYPE_FLOAT',
          'TYPE_BOOLEAN',
          'TYPE_VOID',
          'IF',
          'ELSE',
          'WHILE',
          'FOR',
          'RETURN',
          'BREAK',
          'CONTINUE',
          'NULL',
          'TRUE',
          'FALSE',
          'THIS',
          'SUPER',
          'NEW',
          'ID',
          'INT_CONST',
          'FLOAT_CONST',
          'STRING_CONST',
          'SL_COMMENT',
          'ML_COMMENT'
          )

# Reserved Keywords Dictionary
reserved = {'boolean' : 'TYPE_BOOLEAN',
            'break' : 'BREAK',
            'continue' : 'CONTINUE',
            'class' : 'CLASS',
            'else' : 'ELSE',
            'extends' : 'EXTENDS',
            'false' : 'FALSE',
            'float' : 'TYPE_FLOAT',
            'for' : 'FOR',
            'if' : 'IF',
            'int' : 'TYPE_INT',
            'new' : 'NEW',
            'null' : 'NULL',
            'private' : 'PRIVATE',
            'public' : 'PUBLIC',
            'return' : 'RETURN',
            'static' : 'STATIC',
            'super' : 'SUPER',
            'this' : 'THIS',
            'true' : 'TRUE',
            'void' : 'TYPE_VOID',
            'while' : 'WHILE'}

# Token definitions
t_LEFT_CB = r'{'
t_RIGHT_CB = r'}'
t_LEFT_SQB = r'\['
t_RIGHT_SQB = r']'
t_LEFT_PN = r'\('
t_RIGHT_PN = r'\)'
t_SEMI_COLON = r';'
t_COMMA = r','
t_DOT = r'\.'
t_PLUS = r'\+'
t_MINUS = r'-'
t_STAR = r'\*'
t_F_SLASH = r'/'
t_ASSIGN = r'='
t_INCREMENT = r'\+\+'
t_DECREMENT = r'--'
t_AND = r'&&'
t_OR = r'\|\|'
t_NOT = r'!'
t_EQ = r'=='
t_NOT_EQ = r'!='
t_LT = r'<'
t_LTE = r'<='
t_GT = r'>'
t_GTE = r'>='

def t_ID(t):
    r'[a-zA-z][a-zA-Z0-9_]*'
    if t.value in reserved:
        t.type = reserved[t.value]
    return t

def t_FLOAT_CONST(t):
    r'[0-9]+\.[0-9]+'
    try:
        t.value = float(t.value)
    except Exception as e:
        print('value could not be converted to float, %d', t.value)
        print(e)
        t.value = 0.0
    return t

def t_INT_CONST(t):
    r'[0-9]+'
    try:
        t.value = int(t.value)
    except ValueError as ve:
        print('Integer value too large, %d', t.value)
        print(ve)
        t.value = 0
    return t

def t_STRING_CONST(t):
    r'\".*\"'
    return t

def t_SL_COMMENT(t):
    r'//.*'
    pass

def t_ML_COMMENT(t):
    r'/\*(.|\n)*?\*/'
    pass

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def find_column(input, token):
    line_start = input.rfind('\n', 0, token.lexpos)
    return (token.lexpos - line_start)

t_ignore = ' \t'

def t_error(t):
    print()
    print("LEXER: SYNTAX ERROR: ", end = '')
    print("Illegal character '%s' at line %d" % (t.value[0], t.lexer.lineno))
    print("CONTEXT: " + t.value[0:10])
    print()
    sys.exit()
    #t.lexer.skip(1)

