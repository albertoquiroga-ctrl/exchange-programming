# Exchange Programming - Big Data Programming Intro

This repository contains my exercises for the Introduction to Big Data Programming exchange class.  
Each Python script mirrors one lesson topic: data types, variables, functions, conditionals, loops, collections, random utilities, dictionaries, and while-loop practice.

## Getting Started

1. Install Python 3.10 or newer.
2. (Optional) Create a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On macOS/Linux use: source .venv/bin/activate
   ```
3. Run any script with `python <file_name>.py`.
4. Interactive files wait for stdin. Provide values at the prompts or redirect sample input when testing.

## Repository Map

| Path | Topic or highlight |
| --- | --- |
| `a1-1-datatype.py` | Literal and type experiments for integers and strings. |
| `a1-2-variable.py` | Variable assignment drills (practice lines left commented). |
| `a1-3-buildin.py` | Practice with `print`, `input`, `format`, and BMI style prompts. |
| `a1-4-function.py` | Function basics: greetings plus area helpers. |
| `a1-5-conditional.py` | BMI feedback driven by if/elif/else. |
| `a1-6-bmiCalculator.py` | Interactive BMI calculator with recursion and guards. |
| `a2-1-list.py` | Creating, indexing, mutating, and extending Python lists. |
| `a2-2-random.py` | Sampling integers and colors with the `random` module. |
| `a2-3-loop.py` | `for` loop walkthrough plus break, continue, pass prompts. |
| `a2-4-guessLuckyColor.py` | Guessing game using lists, loops, and randomness. |
| `a3-1-dict.py` | Dictionary creation, updates, deletion, and nesting. |
| `a3-2-loop.py` | Looping through dictionary keys, values, and items. |
| `a3-3-error.py` | Input parsing with try/except and validation messages. |
| `a3-4-whileLoop` | Multiple `while` loop demos (file without extension). |
| `class2_ex_function.py` | Finance themed helpers (circumference, BMI, P/E, etc.). |
| `class3_ex_conditional.py` | Conditional practice: parity, comparisons, leap years, triangles. |
| `class3_ex_list.py` | List helpers for sorted unions and length counting. |
| `class4_ex_library_random.py` | Random number utilities plus `math.sqrt` practice. |
| `class4_ex_loop.py` | Loop utilities for ticker filters, incomes, and percentage change. |
| `class5_ex_dict.py` | Dictionary toolkit (portfolio merges, returns, aggregations). |
| `class5_ex_whileloop.py` | While-only reimplementations of prior loop helpers. |
| `hello.py` | Polished BMI CLI app with validation, type hints, and graceful exit paths. |
| `notebook.ipynb` | Jupyter scratch pad for quick experiments. |

> The `classX` exercises follow the auto-grader contract from class. Keep function names and signatures unchanged when refactoring.

## Working With The Exercises

- Interactive prompts: run scripts such as `a2-3-loop.py`, `a2-4-guessLuckyColor.py`, and `hello.py` directly and supply inputs when asked.
- Imports: wrap extra practice code inside `if __name__ == "__main__":` when extending a file so helpers stay importable.
- Testing ideas: reuse helpers like `calculate_daily_percentage_return` or `apply_percentage_increase` inside dedicated unit tests or notebooks.
- Code style: the repo keeps plain Python standard library only; no extra dependencies are required.

## Suggested Next Steps

1. Move frequently used helpers into a shared module to reduce duplication across assignments.
2. Create pytest suites for BMI helpers, ticker filters, and dictionary utilities.
3. Use `notebook.ipynb` to visualize outputs (lists, dictionaries, or rolling returns) with charts once `matplotlib` is installed.
