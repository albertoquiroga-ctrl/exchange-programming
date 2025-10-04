# Class Exercise 5: Dictionary
# Create the functions below EXACTLY as specified.
# ⚠️ AUTO-GRADER CRITICAL WARNING ⚠️
# - Changing function names/parameters will cause 50% score deduction
# - Incorrect return types/formats will result in 0 marks for that question
# - Comments are ignored by Python and auto-grader (you can add your own)


# Question 1
# Function Name: exclude_blacklisted_tickers_dict
#
# Input Parameters:
# - portfolio (dictionary with ticker: quantity, type: dict)
# - blacklist (list of stock tickers to exclude, type: list of strings)
#
# Expected Return Value:
# - A new dictionary excluding all blacklisted tickers (type: dict)
#
#Examples:
# exclude_blacklisted_tickers_dict({'MSFT': 100, 'AAPL': 200}, ['MSFT'])
# > {'AAPL': 200}
# exclude_blacklisted_tickers_dict({'GOOG': 50, 'AMZN': 300}, [])
# > {'GOOG': 50, 'AMZN': 300}
# exclude_blacklisted_tickers_dict({'IBM': 150}, ['IBM', 'TSLA'])
#> {}


# Question 2
# Function Name: sum_holdings_above_threshold
#
# Input Parameters:
# - portfolio (dictionary with ticker: quantity, type: dict)
# - threshold (minimum quantity to include, type: float)
#
# Expected Return Value:
# - Sum of all quantities in the portfolio above the threshold (type: float)
#
# Examples:
# sum_holdings_above_threshold({'A': 500.0, 'B': 200.0}, 300.0)
# > 500.0
# sum_holdings_above_threshold({'C': 150.0, 'D': 250.0}, 200.0)
# > 250.0
# sum_holdings_above_threshold({'E': 100.0}, 150.0)
# > 0.0


# Question 3
# Function Name: average_transaction_value
#
# Input Parameters:
# - transactions (dictionary with transaction IDs as keys and amounts as values, type: dict)
#
# Expected Return Value:
# - Average transaction amount (type: float). Return 0.0 if empty.
#
# Examples:
# average_transaction_value({'T1': 100.0, 'T2': 200.0})
# > 150.0
# average_transaction_value({'T3': 500.0})
# > 500.0
# average_transaction_value({})
# > 0.0


# Question 4
# Function Name: count_transactions_above_average
#
# Input Parameters:
# - transactions (dictionary with transaction IDs as keys and amounts as values, type: dict)
#
# Expected Return Value:
# - Number of transactions above the average amount (type: int)
#
# Examples:
# count_transactions_above_average({'T1': 100, 'T2': 200, 'T3': 300})
# > 1
# count_transactions_above_average({'T4': 150, 'T5': 150})
# > 0
# count_transactions_above_average({'T6': 500})
# > 0


# Question 5
# Function Name: calculate_daily_returns
#
# Input Parameters:
# - prices (dictionary with dates as keys and prices as values, type: dict)
#
# Expected Return Value:
# - Dictionary of daily percentage returns (rounded to two decimals) for dates after the first (type: dict)
#
# Examples:
# calculate_daily_returns({'2023-01-01': 100.0, '2023-01-02': 105.0})
# > {'2023-01-02': 5.0}
# calculate_daily_returns({'2023-02-01': 200.0, '2023-02-02': 220.0, '2023-02-03': 210.0})
# > {'2023-02-02': 10.0, '2023-02-03': -4.55}
# calculate_daily_returns({'2023-03-01': 50.0})
# > {}


# Question 6
# Function Name: merge_portfolios
#
# Input Parameters:
# - portfolio1 (dictionary with ticker: quantity, type: dict)
# - portfolio2 (dictionary with ticker: quantity, type: dict)
#
# Expected Return Value:
# - Merged dictionary with summed quantities for common tickers (type: dict)
#
# Examples:
# merge_portfolios({'AAPL': 50}, {'AAPL': 30, 'MSFT': 100})
# > {'AAPL': 80, 'MSFT': 100}
# merge_portfolios({'X': 200}, {'Y': 300})
# > {'X': 200, 'Y': 300}
# merge_portfolios({}, {'Z': 150})
# > {'Z': 150}


# Question 7
# Function Name: apply_percentage_increase
#
# Input Parameters:
# - portfolio (dictionary with ticker: current price, type: dict)
# - percentage (percentage increase to apply, type: float)
#
# Expected Return Value:
# - New dictionary with prices increased by specified percentage (rounded to two decimals, type: dict)
# Examples:
# apply_percentage_increase({'AAPL': 100.0}, 10.0)
# > {'AAPL': 110.0}
# apply_percentage_increase({'MSFT': 50.0, 'GOOG': 200.0}, 5.0)
# > {'MSFT': 52.5, 'GOOG': 210.0}
# apply_percentage_increase({}, 20.0)
# > {}


# Question 8
# Function Name: find_max_holding
#
# Input Parameters:
# - portfolio (dictionary with ticker: quantity, type: dict)
#
# Expected Return Value:
# - Ticker with the highest quantity (first occurrence if tie, None if empty, type: str)
#
# Examples:
# find_max_holding({'A': 500, 'B': 700})
# > 'B'
# find_max_holding({'X': 100, 'Y': 100})
# > 'X'
# find_max_holding({})
# > None