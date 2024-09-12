# Compiler Design Project

This repository contains the implementation of a one-pass compiler for a modified version of the C-minus programming language. The compiler is developed in four phases, with each phase focusing on one of the main modules: lexical analysis, syntax analysis, semantic analysis, and intermediate code generation.

## Table of Contents

- [Project Overview](#project-overview)
- [Compiler Phases](#compiler-phases)
  - [Phase 1: Lexical Analysis (Scanner)](#phase-1-lexical-analysis-scanner)
  - [Phase 2: Syntax Analysis (Parser)](#phase-2-syntax-analysis-parser)
  - [Phase 3: Semantic Analysis](#phase-3-semantic-analysis)
  - [Phase 4: Intermediate Code Generation](#phase-4-intermediate-code-generation)
- [Testing](#testing)
- [References](#references)

## Project Overview

The goal of this project is to implement a one-pass compiler for the C-minus language. The compiler consists of four main modules that work together in a pipeline fashion, processing the input program from lexical analysis to code generation. 

### Compiler Structure

- **One-Pass Compilation**: The input program is read only once, and all modules work sequentially to generate the desired output.
- **Input File**: A C-minus program provided through `input.txt`.
- **Output**: The compiler produces several outputs, including tokenized files, parse trees, error logs, symbol tables, and intermediate code.

## Compiler Phases

### Phase 1: Lexical Analysis (Scanner)

**Objective**: Implement a scanner that tokenizes the input C-minus program.

- **Input**: `input.txt` - A text file containing a C-minus program.
- **Output**:
  - `tokens.txt` - Tokenized form of the input, listing recognized tokens line-by-line.
  - `lexical_errors.txt` - Logs of any lexical errors detected, such as invalid characters or unmatched comments.
  - `symbol_table.txt` - A table of recognized identifiers and keywords.
  
**Error Handling**: The scanner uses Panic Mode to handle lexical errors and continues scanning after recovering from errors.

### Phase 2: Syntax Analysis (Parser)

**Objective**: Develop an LL(1) predictive top-down parser to generate a parse tree for the C-minus program.

- **Input**: `input.txt` - A C-minus program to be scanned and parsed.
- **Output**:
  - `parse_tree.txt` - A formatted parse tree of the input program.
  - `syntax_errors.txt` - Logs of any syntax errors detected during parsing.
  
**Error Handling**: The parser uses Panic Mode, leveraging the follow set of each non-terminal as its synchronizing set to recover from syntax errors.

### Phase 3: Semantic Analysis

**Objective**: Analyze the program's semantics, checking for semantic errors and generating a symbol table with detailed information.

- **Output**:
  - `semantic_errors.txt` - Logs of semantic errors such as type mismatches, undeclared variables, etc.
  - Updates to `symbol_table.txt` - Includes type and arity information for identifiers.
  
**Error Handling**: Handles semantic errors gracefully, allowing continued analysis and reporting all detected issues.

### Phase 4: Intermediate Code Generation

**Objective**: Generate intermediate code that represents the C-minus program in a lower-level form suitable for interpretation or further compilation.

- **Output**: 
  - `intermediate_code.txt` - The intermediate representation of the input program.
  
**Approach**: Uses the semantic information and syntax tree to produce code that can be executed by a tester interpreter.

## Testing

Each module of the compiler is tested using various C-minus programs to ensure correctness, robustness, and proper error handling. Sample inputs and expected outputs are provided in the `tests` directory.

## References

- [1] Wang, Q., & Davis, M. (2003). C-minus Compiler Specifications. Journal of Computer Languages, Systems & Structures.
- [Lecture Notes](#) on LL(1) parsing, Panic Mode error recovery, and intermediate code generation.
