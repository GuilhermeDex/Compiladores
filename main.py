import re
import sys

#Lista das palavras reservadas
KEYWORDS = {'if', 'else', 'while', 'for', 'return', 'int', 'float', 'char', 'void','auto', 'case', 'else', 'const','double', 'long'}
#Lista dos operadores
OPERATORS = {'+', '-', '*', '/', '=', '==', '!=', '<', '<=', '>', '>=', '+=', '%','-=','&&','!','++','--'}
#Lista dos separadores
SEPARATORS = {'(', ')', '{', '}', '[', ']', ',', ';'}

#Especificao dos tokens
token_specification = [
    ('NUMBER',   r'\d+(\.\d+)?'),
    ('ID',       r'[A-Za-z_]\w*'),
    ('OP',       r'==|!=|<=|>=|[+\-*/=<>]'),
    ('SEP',      r'[()[\]{};,]'),
    ('SKIP',     r'[ \t]+'),
    ('NEWLINE',  r'\n'),
    ('COMMENT',  r'//.*'),
]


#Compilando o REGEX
tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)
get_token = re.compile(tok_regex).match

def lexer(code):
    pos = 0
    line = 1
    col = 1
    tokens = []
    while pos < len(code):
        mo = get_token(code, pos)
        if mo:
            kind = mo.lastgroup
            value = mo.group()

            if kind == 'NEWLINE':
                line += 1
                col = 1
                pos = mo.end()
                continue
            elif kind == 'SKIP' or kind == 'COMMENT':               #Caso tenha algum comentario apenas ignorar
                pass
            elif kind == 'NUMBER':
                tokens.append(('NUMBER', value))
            elif kind == 'ID':
                if value in KEYWORDS:
                    tokens.append(('KEYWORD', value))
                else:
                    tokens.append(('IDENTIFIER', value))
            elif kind == 'OP':
                tokens.append(('OPERATOR', value))
            elif kind == 'SEP':
                tokens.append(('SEPARATOR', value))
            else:
                raise RuntimeError(f'Token inesperado ({value}) na linha {line}, coluna {col}')         #Caso tenha algum token inesperado aparecera um erro
            
            advance = mo.end() - mo.start()
            pos = mo.end()
            col += advance
        else:
            error_char = code[pos]
            raise RuntimeError(f'Erro lexico: caractere invalido "{error_char}" na linha {line}, coluna {col}')
    return tokens

#lendo o Arquivo.txt
if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(1)

    filename = sys.argv[1]

    with open(filename, 'r') as f:
        code = f.read()

    try:
        tokens = lexer(code)
        for tipo, valor in tokens:
            print(f'{tipo:12} -> {valor}')
    except RuntimeError as e:
        print(e)