# COMPILADORES
```c
#define AUTOR ["Guilherme Francis"]
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

## 🤖 Como é realizado os testes
Começamos lendo o exemplo do código que esta no arquivo.txt, com isso conseguimos ler token por token e ir armazenando em uma lista, no final temos o resultado mostrando extamente o que cada token significa, podendo ser uma KEYWORD, identificador, operador, separador e um numero!

---

## 🚀 Como rodar

### Pré-requisitos

- Python 3 instalado
- Terminal recomendado: linux ou WSL

### Usando o Makefile

```bash
make        # Executa o analisador léxico com input.txt
```




&nbsp;