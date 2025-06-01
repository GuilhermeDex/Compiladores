import re
import sys

#Lista das palavras reservadas
KEYWORDS = {'if', 'else', 'while', 'for', 'return', 'int', 'float', 'char', 'void','auto', 'case', 'else', 'const','double', 'long'}
#Lista dos operadores
OPERATORS = {'+', '-', '*', '/', '=', '==', '!=', '<', '<=', '>', '>=', '+=', '%', '-=', '&&', '!', '++', '--',}
#Lista dos separadores
SEPARATORS = {'(', ')', '{', '}', '[', ']', ',', ';'}

#Especificao dos tokens
token_specification = [
    ('NUMBER',   r'\d+(\.\d+)?'),
    ('ID',       r'[A-Za-z_]\w*'),
    ('OP',       r'==|!=|<=|>=|[+\-*/=%!<>]'),
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
            elif kind == 'SKIP' or kind == 'COMMENT':               #caso tenha algum comentario apenas ignorar
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
                raise RuntimeError(f'Token inesperado ({value}) na linha {line}, coluna {col}')         #caso tenha algum token inesperado aparecera um erro
            
            advance = mo.end() - mo.start()
            pos = mo.end()
            col += advance
        else:
            error_char = code[pos]
            raise RuntimeError(f'Erro lexico: caractere invalido "{error_char}" na linha {line}, coluna {col}')
    return tokens

def log(categoria, mensagem):
    tag = f"[{categoria.upper():<10}]"
    print(f"{tag} {mensagem}")

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def match(self, expected_type, expected_value=None):
        if self.pos < len(self.tokens):
            token_type, token_value = self.tokens[self.pos]
            if token_type == expected_type and (expected_value is None or token_value == expected_value):
                self.pos += 1
                return token_value
        return None

    def expect(self, expected_type, expected_value=None):
        result = self.match(expected_type, expected_value)
        if result is None:
            expected = expected_value if expected_value else expected_type
            current = self.tokens[self.pos] if self.pos < len(self.tokens) else ('EOF', '')
            raise SyntaxError(f"Esperado {expected}, mas encontrado {current}")
        return result

    def parse(self):
        while self.pos < len(self.tokens):
            self.statement()

    def statement(self):
        if self.check('KEYWORD', 'if'):
            self.if_stmt()
        elif self.check('KEYWORD', 'while'):
            self.while_stmt()
        elif self.check('KEYWORD', 'return'):
            self.return_stmt()
        elif self.check('KEYWORD'):
            self.declaration()
        elif self.check('IDENTIFIER'):
            self.assignment()
        elif self.check('SEPARATOR', '{'):
            self.block()
        else:
            raise SyntaxError(f"Declaracao invalida em {self.tokens[self.pos]}")

    def if_stmt(self):
        self.expect('KEYWORD', 'if')
        log("estrutura", "if com condicao:")
        self.expect('SEPARATOR', '(')
        self.expression()
        self.expect('SEPARATOR', ')')
        self.statement()
        if self.match('KEYWORD', 'else'):
            log("estrutura", "else")
            self.statement()

    def while_stmt(self):
        self.expect('KEYWORD', 'while')
        log("estrutura", "while com condicao:")
        self.expect('SEPARATOR', '(')
        self.expression()
        self.expect('SEPARATOR', ')')
        self.statement()

    def return_stmt(self):
        self.expect('KEYWORD', 'return')
        log("comando", "return com expressao:")
        self.expression()
        self.expect('SEPARATOR', ';')

    def declaration(self):
        tipo = self.expect('KEYWORD')
        nome = self.expect('IDENTIFIER')
        log("declaracao", f"Tipo: {tipo}, Nome: {nome}")
        if self.match('OPERATOR', '='):
            log("inicializacao", f"Variavel: {nome} com expressao:")
            self.expression()
        self.expect('SEPARATOR', ';')

    def assignment(self):
        var = self.expect('IDENTIFIER')
        self.expect('OPERATOR', '=')
        log("atribuicao", f"Variavel: {var} recebe expressao:")
        self.expression()
        self.expect('SEPARATOR', ';')

    def block(self):
        self.expect('SEPARATOR', '{')
        log("bloco", "Inicio de bloco {")
        while not self.check('SEPARATOR', '}'):
            self.statement()
        self.expect('SEPARATOR', '}')
        log("bloco", "Fim de bloco }")

    def expression(self):
        log("expressao", "analisando expressao")
        self.simple_expression()
        while self.match('OPERATOR', '==') or self.match('OPERATOR', '!=') or \
              self.match('OPERATOR', '<') or self.match('OPERATOR', '<=') or \
              self.match('OPERATOR', '>') or self.match('OPERATOR', '>='):
            log("expressao", "operador relacional encontrado")
            self.simple_expression()

    def simple_expression(self):
        self.term()
        while self.match('OPERATOR', '+') or self.match('OPERATOR', '-'):
            log("expressao", "operador aditivo encontrado")
            self.term()

    def term(self):
        self.factor()
        while self.match('OPERATOR', '*') or self.match('OPERATOR', '/'):
            self.factor()

    def factor(self):
        if self.match('IDENTIFIER'):
            log("fator", "Identificador")
        elif self.match('NUMBER'):
            log("fator", "Numero")
        elif self.match('SEPARATOR', '('):
            log("fator", "Expressao entre parenteses")
            self.expression()
            self.expect('SEPARATOR', ')')
        else:
            raise SyntaxError(f"Fator invalido em {self.tokens[self.pos]}")

    def check(self, expected_type, expected_value=None):
        if self.pos < len(self.tokens):
            token_type, token_value = self.tokens[self.pos]
            return token_type == expected_type and (expected_value is None or token_value == expected_value)
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python analisador.py arquivo.txt")
        sys.exit(1)

    filename = sys.argv[1]
    with open(filename, 'r') as f:
        code = f.read()

    try:
        tokens = lexer(code)
        parser = Parser(tokens)
        parser.parse()
        print("Analise sintatica concluida com sucesso!")
    except RuntimeError as e:
        print(f"Erro lexico: {e}")
    except SyntaxError as e:
        print(f"Erro sintatico: {e}")