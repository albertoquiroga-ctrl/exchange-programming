# Exchange Programming - Big Data Programming Intro

A consolidated workspace for my exchange-course exercises. It tracks every lecture lab, follow-up exercise, notebook, and supporting reference that I used while learning Python for big-data analytics.

## Highlights
- Covers the full lecture progression from literals and control flow through API usage and data wrangling.
- Includes standalone exercises for API integrations (RapidAPI, CoinMarketCap, Yahoo Finance) and finance-themed helpers.
- Provides Jupyter notebooks plus sample CSV data for pandas practice and data-joining walkthroughs.
- Keeps course slides, references, and the final project deliverable alongside the code for quick lookup.

## Environment Setup
1. Install **Python 3.10+**.
2. (Optional) Create and activate a virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```
3. Install the libraries that power the data work. Start with the essentials below and add more as a script demands it:
   ```powershell
   python -m pip install pandas yfinance requests jupyter
   ```
4. Run a script with `python <path-to-file>.py` or open the notebooks inside Jupyter/Lab.

## Repository Layout

### Lecture scripts (`Intro to Python Lectures/`)
| Path | Topic snapshot |
| --- | --- |
| `Intro to Python Lectures/a1-1-datatype.py` | Playing with literals, numeric types, and casting. |
| `Intro to Python Lectures/a1-6-bmiCalculator.py` | Early BMI calculator with recursion and guard clauses. |
| `Intro to Python Lectures/a2-1-list.py` to `a2-4-guessLuckyColor.py` | List basics, random sampling, for-loops, and guessing games. |
| `Intro to Python Lectures/a3-1-dict.py` to `a3-4-whileLoop` | Dictionaries, loop patterns, and error handling practice. |
| `Intro to Python Lectures/a6_datatime.py` & `a6_yfinance_example.py` | Mini labs showing `datetime`, `pandas`, and `yfinance`. |
| `Intro to Python Lectures/property.html`, `clientlib-all.js` | Small HTML/JS asset used during lecture demos. |

### Exercise set (`Excercises/`)
| Path | Focus |
| --- | --- |
| `Excercises/assignment1.py` | Consolidated warm-up covering formatting, math helpers, and input handling. |
| `Excercises/class2_ex_function.py` | Financial helper functions (circumference, BMI, PE ratios). |
| `Excercises/class3_ex_conditional.py` & `class3_ex_list.py` | Conditional drills (parity, leap years) and list utilities. |
| `Excercises/class4_ex_library_random.py` & `class4_ex_loop.py` | Random number helpers, ticker filters, and loop practice. |
| `Excercises/class5_ex_dict.py` & `class5_ex_whileloop.py` | Portfolio-style dictionary manipulation and while-only rewrites. |
| `Excercises/class6_ex_if_q1.py` to `class6_ex_try_q2.py` | Validation, guards, and `try/except` exercises. |
| `Excercises/class6_ex_yfinance.py` | Weekly return analysis that fetches prices directly from Yahoo Finance. |
| `Excercises/coinmarketcap.py` & `Rapid_API_Forex_question.py` | API-driven price lookups (CoinMarketCap, RapidAPI ExchangeRate). |
| `Excercises/HSBC_valuation*.py`, `hktvmall_question.py` | Finance case studies and problem-specific helpers. |

### Data notebooks (`Working with Dataframe (new)/`)
| Path | Description |
| --- | --- |
| `Working with Dataframe (new)/1. Working with Dataframe.ipynb` | Intro to pandas Series/DataFrame transforms using `walmart_stock.csv`. |
| `Working with Dataframe (new)/2. Joining Data Example.ipynb` | Join and merge walkthroughs backed by `state-*.csv` reference files. |
| `Working with Dataframe (new)/3. Combine data with different timeframe.ipynb` | Resampling and alignment practice with `AAPL*.csv`, `hibor.csv`, and `quarterly_data.csv`. |
| All CSV files in this folder | Sample datasets kept under version control for offline experimentation. |

### Final deliverables & references
| Path | Purpose |
| --- | --- |
| `Final Project/ECON7890 Project 2025 Fall.pdf` | Final project write-up. |
| `ECON7890 - Course Intro - 202509.pdf`, `ECON7890 - Python and Tools.pdf`, `ECON 7890_Big_Data_Analytics_Programming_20190710.pdf` | Slide decks and course material PDFs. |
| `References/pythonlearn (1).pdf` | Additional reading (Think Python companion). |

## Working With The Material
- **Run lecture/exercise scripts**: `python ".\Intro to Python Lectures\a2-3-loop.py"` or `python ".\Excercises\class4_ex_loop.py"`. Interactive prompts will pause until you provide input.
- **Import helpers elsewhere**: Keep experimentation code inside `if __name__ == "__main__":` blocks so functions remain reusable from notebooks or other modules.
- **Use notebooks for exploration**: `jupyter notebook "Working with Dataframe (new)"` opens the pandas labs with the curated CSV files already co-located.
- **Version control friendly experiments**: store new drafts inside `Excercises/` or create a new notebook to avoid modifying the canonical lecture files.

## External Data & API Notes
- Scripts that call Yahoo Finance (`Intro to Python Lectures/a6_yfinance_example.py`, `Excercises/class6_ex_yfinance.py`) require network access plus `pandas` and `yfinance`.
- `Excercises/coinmarketcap.py` expects a `COINMARKETCAP_API_KEY` env variable (falls back to the demo key currently checked in).
- `Excercises/Rapid_API_Forex_question.py` reads `RAPIDAPI_KEY` for the ExchangeRate API; update the default constant or export your own key before running.
- Notebook CSVs are bundled locally, so pandas can load them without extra downloads.

## Suggested Next Steps
1. Promote shared helpers (BMI, ticker filters, conversions) into a small package or module to cut repetition.
2. Add pytest smoke tests for the deterministic utilities before refactoring them for new assignments.
3. Extend the notebooks with visualizations (matplotlib, seaborn) or additional API data once the basics run smoothly.
