# Class Exercise 5: Dictionary
# Create the functions below EXACTLY as specified.
#  AUTO-GRADER CRITICAL WARNING
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
def exclude_blacklisted_tickers_dict(portfolio, blacklist):
    """Return a new portfolio dictionary excluding blacklisted tickers."""
    return {ticker: quantity for ticker, quantity in portfolio.items() if ticker not in blacklist}

print("exclude_blacklisted_tickers_dict:", exclude_blacklisted_tickers_dict({'MSFT': 100, 'AAPL': 200}, ['MSFT']))


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
def sum_holdings_above_threshold(portfolio, threshold):
    """Sum holdings that are strictly above the given threshold."""
    total = sum(quantity for quantity in portfolio.values() if quantity > threshold)
    return float(total)

print("sum_holdings_above_threshold:", sum_holdings_above_threshold({'A': 500.0, 'B': 200.0}, 300.0))


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
def average_transaction_value(transactions):
    """Compute the average value of transactions; return 0.0 when empty."""
    if not transactions:
        return 0.0
    total = sum(transactions.values())
    return float(total) / len(transactions)

print("average_transaction_value:", average_transaction_value({'T1': 100.0, 'T2': 200.0}))


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
def count_transactions_above_average(transactions):
    """Count how many transactions are strictly above the average amount."""
    if not transactions:
        return 0
    average_value = average_transaction_value(transactions)
    return sum(1 for amount in transactions.values() if amount > average_value)

print("count_transactions_above_average:", count_transactions_above_average({'T1': 100, 'T2': 200, 'T3': 300}))


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
def calculate_daily_returns(prices):
    """Calculate day-over-day percentage returns rounded to two decimals."""
    items = list(prices.items())
    daily_returns = {}
    for index in range(1, len(items)):
        _, previous_price = items[index - 1]
        current_date, current_price = items[index]
        if previous_price == 0:
            change = 0.0
        else:
            change = ((current_price - previous_price) / previous_price) * 100
        daily_returns[current_date] = round(change, 2)
    return daily_returns

print("calculate_daily_returns:", calculate_daily_returns({'2023-02-01': 200.0, '2023-02-02': 220.0, '2023-02-03': 210.0}))


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
def merge_portfolios(portfolio1, portfolio2):
    """Merge two portfolios, summing quantities for duplicate tickers."""
    merged = dict(portfolio1)
    for ticker, quantity in portfolio2.items():
        merged[ticker] = merged.get(ticker, 0) + quantity
    return merged

print("merge_portfolios:", merge_portfolios({'AAPL': 50}, {'AAPL': 30, 'MSFT': 100}))


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
def apply_percentage_increase(portfolio, percentage):
    """Increase each ticker price by the given percentage, rounded to two decimals."""
    factor = 1 + (percentage / 100)
    return {ticker: round(price * factor, 2) for ticker, price in portfolio.items()}

print("apply_percentage_increase:", apply_percentage_increase({'MSFT': 50.0, 'GOOG': 200.0}, 5.0))


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
def find_max_holding(portfolio):
    """Return the ticker with the highest quantity (first occurrence on ties)."""
    if not portfolio:
        return None
    max_ticker = None
    max_quantity = None
    for ticker, quantity in portfolio.items():
        if max_quantity is None or quantity > max_quantity:
            max_ticker = ticker
            max_quantity = quantity
    return max_ticker

print("find_max_holding:", find_max_holding({'A': 500, 'B': 700}))
