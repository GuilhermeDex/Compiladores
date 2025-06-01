# COMPILADORES
```c
#define AUTOR "Guilherme Francis"
#define DISCIPLINA "Compiladores"
#define PROFESSOR "Flávio Schiavoni"
```

## 🔤 Analisador Léxico em Python

Este projeto é um **analisador léxico** escrito em Python, feito como parte de uma disciplina de Compiladores.

O analisador lê um código-fonte simples (em estilo C) e quebra ele em **tokens**: palavras-chave, identificadores, operadores, separadores, números, etc.

Se encontrar algo inválido, ele exibe um erro com **linha e coluna** para ajudar na depuração.

---

## 🧠 O que é um analisador léxico?

É a primeira etapa da construção de um compilador. Ele recebe o **código-fonte como texto** e separa em **unidades léxicas significativas**, chamadas de **tokens**. Exemplos de tokens:

- `int`, `return` → palavra-chave (*keyword*)
- `soma`, `i` → identificador
- `+`, `==` → operador
- `(`, `)` → separador
- `123`, `3.14` → número

---
## 📐 Analisador Sintático (Parser)

Além do analisador léxico, este projeto também possui um **analisador sintático** (parser), que é responsável por verificar **a estrutura e a ordem dos tokens** de acordo com a gramática da linguagem.

Ele reconhece estruturas como:

- Declarações de variáveis
- Atribuições
- Expressões aritméticas e relacionais
- Comandos de controle como `if`, `else`, `while`
- `return` e blocos `{ ... }`

O parser foi implementado com a técnica de **analisador sintático recursivo descendente**.

---

## 🔎 Exemplo de estruturas suportadas

```c
int x = 5;
float y;
y = x + 2.5;

if (x > 0) {
    y = y + 1;
} else {
    y = y - 1;
}

while (x < 10) {
    x = x + 1;
}

return x;
```

Durante a análise sintática, o terminal exibe o que foi reconhecido e classifica como `[DECLARACAO]`, `[EXPRESSAO]`, `[FATOR]`, `[ESTRUTURA]`, etc., com todas as tags padronizadas em tamanho para facilitar a leitura.

---

## 🤖 Como é realizado os testes

- O código a ser analisado é salvo no `input.txt`.
- O analisador léxico gera uma lista de tokens.
- O analisador sintático percorre esses tokens verificando se estão **em conformidade com a gramática da linguagem**.
- Toda estrutura reconhecida é exibida no terminal com sua respectiva categoria.

Em caso de erro sintático, é exibida uma mensagem clara indicando o que era esperado e o que foi encontrado.

---

## 🚀 Como rodar

### Pré-requisitos

- Python 3 instalado
- Terminal recomendado: linux ou WSL

### Usando o Makefile

```bash
make        # Executa o analisador léxico com input.txt
```
> Certifique-se de que o arquivo `input.txt` esteja no mesmo diretório com o código de entrada que deseja testar.




&nbsp;