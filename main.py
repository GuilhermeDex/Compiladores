import re
import sys

# Lista das palavras reservadas
KEYWORDS = {'if', 'else', 'while', 'for', 'return', 'int', 'float', 'char', 'void', 'auto', 'case', 'const', 'double', 'long'}
# Lista dos operadores
OPERATORS = {'+', '-', '*', '/', '=', '==', '!=', '<', '<=', '>', '>=', '+=', '%', '-=', '&&', '!', '++', '--'}
# Lista dos separadores
SEPARATORS = {'(', ')', '{', '}', '[', ']', ',', ';'}

# Especificacao dos tokens
token_specification = [
    ('NUMBER',   r'\d+(\.\d+)?'),
    ('ID',       r'[A-Za-z_]\w*'),
    ('OP',       r'==|!=|<=|>=|[+\-*/=%!<>]'),
    ('SEP',      r'[()[\]{};,]'),
    ('SKIP',     r'[ \t]+'),
    ('NEWLINE',  r'\n'),
    ('COMMENT',  r'//.*'),
]

# Compilando o REGEX
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
            elif kind == 'SKIP' or kind == 'COMMENT':
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
                raise RuntimeError(f'Token inesperado ({value}) na linha {line}, coluna {col}')
            
            advance = mo.end() - mo.start()
            pos = mo.end()
            col += advance
        else:
            error_char = code[pos]
            raise RuntimeError(f'Erro léxico: caractere invalido "{error_char}" na linha {line}, coluna {col}')
    return tokens

def log(categoria, mensagem):
    tag = f"[{categoria.upper():<10}]"
    print(f"{tag} {mensagem}")


class CodeGenerator:
    def __init__(self):
        self.lines = []
        self.indent = 0

    def emit(self, line):
        self.lines.append('    ' * self.indent + line)

    def open_block(self):
        self.emit('{')
        self.indent += 1

    def close_block(self):
        self.indent -= 1
        self.emit('}')

    def get_code(self):
        return '\n'.join(self.lines)


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.scopes = [{}]  # pilha de escopos
        self.codegen = CodeGenerator()
        self.const_table = {}  # Para propagacao de constantes


    def current_scope(self):
        return self.scopes[-1]

    def add_symbol(self, name, tipo):
        if name in self.current_scope():
            raise SyntaxError(f"Variavel '{name}' ja declarada no escopo atual")
        self.current_scope()[name] = tipo

    def find_symbol(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise SyntaxError(f"Variavel '{name}' nao declarada")

    def infer_type(self, valor):
        try:
            float_val = float(valor)
            return 'float' if '.' in valor else 'int'
        except:
            return 'unknown'
 

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
        self.add_symbol(nome, tipo)
        log("declaraçao", f"Tipo: {tipo}, Nome: {nome}")
        self.codegen.emit(f"{tipo} {nome};")
        if self.match('OPERATOR', '='):
            expr, valor_tipo = self.expression()
            if not self.check_type_compatibility(tipo, valor_tipo):
                raise SyntaxError(f"Incompatibilidade de tipo: esperado {tipo}, mas recebeu {valor_tipo}")
            if expr.isdigit():
                self.const_table[nome] = expr  #  salva valor para propagação
            else:
                self.const_table.pop(nome, None)
            self.codegen.emit(f"{nome} = {expr};")
        self.expect('SEPARATOR', ';')

    def assignment(self):
        var = self.expect('IDENTIFIER')
        tipo_var = self.find_symbol(var)
        self.expect('OPERATOR', '=')
        valor, valor_tipo = self.expression()
        if not self.check_type_compatibility(tipo_var, valor_tipo):
            raise SyntaxError(f"Incompatibilidade de tipo na atribuiçao de '{var}': esperado {tipo_var}, mas recebeu {valor_tipo}")
        if valor.isdigit():                      # salvar valor constante se for numerico
            self.const_table[var] = valor
        else:
            self.const_table.pop(var, None)
        self.codegen.emit(f"{var} = {valor};")
        self.expect('SEPARATOR', ';') 


    def block(self):
        self.expect('SEPARATOR', '{')
        log("bloco", "Início de bloco {")
        self.scopes.append({})
        self.codegen.open_block()
        while not self.check('SEPARATOR', '}'):
            self.statement()
        self.expect('SEPARATOR', '}')
        self.scopes.pop()
        self.codegen.close_block()
        log("bloco", "Fim de bloco }")

    def expression(self):
        log("expressao", "analisando expressao")
        expr, tipo = self.simple_expression()
        while self.match('OPERATOR', '==') or self.match('OPERATOR', '!=') or \
            self.match('OPERATOR', '<') or self.match('OPERATOR', '<=') or \
            self.match('OPERATOR', '>') or self.match('OPERATOR', '>='):
            log("expressao", "operador relacional encontrado")
            right, _ = self.simple_expression()
            expr = f"{expr} {self.tokens[self.pos - 1][1]} {right}"
            tipo = 'int'
        return expr, tipo


    def simple_expression(self):
        left = self.term()
        tipo_left = self.infer_type(left)
        while self.check('OPERATOR', '+') or self.check('OPERATOR', '-'):
            op = self.expect('OPERATOR')
            right = self.term()
            tipo_right = self.infer_type(right)
            try:
                result = str(eval(f"{left} {op} {right}"))                           # otimizacao de folding que eh quando ja faz a soma ou subtcao de uma variavel direto
                log("otimizacao", f"Folding: {left} {op} {right} => {result}")
                left = result
                tipo_left = self.infer_type(result)
            except:
                left = f"{left} {op} {right}"
                tipo_left = 'float' if 'float' in (tipo_left, tipo_right) else 'int'
        return left, tipo_left


    def term(self):
        tipo = self.factor()
        while self.check('OPERATOR', '*') or self.check('OPERATOR', '/'):
            op = self.expect('OPERATOR')
            tipo_direito = self.factor()
            if tipo == 'float' or tipo_direito == 'float':
                tipo = 'float'
            else:
                tipo = 'int'

        return tipo


    def factor(self):
        if self.check('IDENTIFIER'):
            nome = self.expect('IDENTIFIER')
            log("fator", f"Identificador {nome}")
            self.find_symbol(nome)
            if nome in self.const_table:
                log("propagacao", f"Substituindo {nome} por constante {self.const_table[nome]}")                        #propagacao na leitura de variaveis
                return self.const_table[nome]
            return nome
        elif self.check('NUMBER'):
            valor = self.expect('NUMBER')
            log("fator", f"Numero {valor}")
            return valor
        elif self.match('SEPARATOR', '('):
            log("fator", "Expressao entre parenteses")
            expr = self.expression()
            self.expect('SEPARATOR', ')')
            return f"({expr})"
        else:
            raise SyntaxError(f"Fator invalido em {self.tokens[self.pos]}")

    def check_type_compatibility(self, tipo1, tipo2):
        if tipo1 == tipo2:
            return True
        if tipo1 == 'float' and tipo2 == 'int':
            return True
        return False

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
        print("Analise sintatica e semantica concluida com sucesso!")
        print("\n--- CODIGO GERADO ---")
        print(parser.codegen.get_code())

    except RuntimeError as e:
        print(f"Erro lexico: {e}")
    except SyntaxError as e:
        print(f"Erro sintatico/semantico: {e}")
