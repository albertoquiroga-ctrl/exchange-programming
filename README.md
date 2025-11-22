# Exchange Programming - Big Data Programming Intro

Course workspace for ECON 7890. It bundles lecture labs, follow-up exercises, pandas notebooks with bundled data, Monte Carlo simulations, the HK Conditions Monitor final project, and LLM API experiments.

## Quick start
1. Install Python 3.10+.
2. (Optional) create and activate a virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```
3. Install common libraries used across the exercises and notebooks:
   ```powershell
   python -m pip install pandas yfinance requests jupyter
   ```
4. Run any script with `python <path>.py` or open the pandas notebooks with `jupyter notebook "Working with Dataframe (new)"`.

### Extra setup for specific folders
- `Final Project/hk_monitor/`: `python -m pip install -r "Final Project/hk_monitor/requirements.txt"` then run `python app.py` from that folder.
- `LLM Integration/`: install `requests python-dotenv openai pandas` and create `.env` with `OPEN_ROUTER_API_KEY`, `MODEL`, `OPEN_ROUTER_HTTP_REFERER` (optional), and `RAPIDAPI_KEY` for tweet fetching.
- `Final Project/Examples/`: scripts rely on extra libs (`pypfopt`, `matplotlib`, `web3`, `beautifulsoup4`, `openai`) and personal API credentials; read each file before running.

## Repository map
- `Intro to Python Lectures/`: fundamentals (datatypes, functions, conditionals, lists, loops), error handling, datetime practice, and a Yahoo Finance mini example. Includes small HTML/JS assets used in class.
- `Excercises/`: three graded assignments plus class drills on functions, conditionals, loops, dictionaries, and while-only rewrites. Includes API helpers for Yahoo Finance weekly returns, CoinMarketCap quotes, RapidAPI forex, and HSBC/hktvmall practice problems.
- `Working with Dataframe (new)/`: three pandas notebooks on series/dataframe transforms, joins, resampling, and alignment. All CSV inputs (AAPL, walmart_stock, hibor, state reference files, etc.) are stored alongside the notebooks.
- `Simulation/`: Monte Carlo odds explorations for coin-flip betting and the Monty Hall problem.
- `LLM Integration/`: OpenRouter client helpers plus scripts to chat (`open_router_conversation.py`), annotate Elon tweets, and categorize Airbnb listing titles using `listings.csv` as input.
- `Final Project/hk_monitor/`: single-file console dashboard that polls live HK warnings, rain, AQHI, and traffic data. See the folder README for controls and code layout.
- `Final Project/Examples/`: short fintech prototypes (portfolio optimization backtest, high-value Ethereum transaction checker, Elon tweet sentiment) with matching writeups in the markdown files.
- `References/` and root PDFs: course slide decks, syllabus, and a Think Python companion PDF.

## External services and keys
- Yahoo Finance scripts need network access plus `pandas` and `yfinance`.
- `Excercises/coinmarketcap.py` reads `COINMARKETCAP_API_KEY`; a demo key is present but you should supply your own.
- RapidAPI keys are used by `Excercises/Rapid_API_Forex_question.py` and `LLM Integration/categorize_elon_tweet.py`.
- OpenRouter keys are required for all `LLM Integration` scripts and `Final Project/Examples/elon_sentiment.py`; set `OPEN_ROUTER_API_KEY` (and `MODEL` if you want to override the default).
- Ethereum example (`Final Project/Examples/blockchain.py`) expects a valid Infura URL or similar node endpoint.
- Avoid committing live secrets; use a local `.env` file instead of hardcoding keys.
