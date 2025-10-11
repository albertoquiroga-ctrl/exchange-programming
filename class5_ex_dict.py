# Class Exercise 5: Dictionary
# Create the functions below EXACTLY as specified.
# ?s???? AUTO-GRADER CRITICAL WARNING ?s????
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
    filtered_portfolio = {}
    for ticker, quantity in portfolio.items():
        is_blacklisted = ticker in blacklist
        if not is_blacklisted:
            filtered_portfolio[ticker] = quantity
    return filtered_portfolio

sample_portfolio_q1 = {'MSFT': 100, 'AAPL': 200, "GOOG": 50}
sample_blacklist_q1 = ['MSFT']
sample_result_q1 = exclude_blacklisted_tickers_dict(sample_portfolio_q1, sample_blacklist_q1)
print("exclude_blacklisted_tickers_dict:", sample_result_q1)


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
    total_quantity = 0.0
    for ticker, quantity in portfolio.items():
        is_above_threshold = quantity > threshold
        if is_above_threshold:
            total_quantity += quantity
    return float(total_quantity)

sample_portfolio_q2 = {'A': 500.0, 'B': 200.0}
sample_threshold_q2 = 300.0
sample_result_q2 = sum_holdings_above_threshold(sample_portfolio_q2, sample_threshold_q2)
print("sum_holdings_above_threshold:", sample_result_q2)


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

    total_amount = 0.0
    transaction_count = 0
    for amount in transactions.values():
        total_amount += amount
        transaction_count += 1

    average_value = total_amount / transaction_count
    return float(average_value)

sample_transactions_q3 = {'T1': 100.0, 'T2': 200.0}
sample_result_q3 = average_transaction_value(sample_transactions_q3)
print("average_transaction_value:", sample_result_q3)


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

    count_above_average = 0
    for amount in transactions.values():
        is_above_average = amount > average_value
        if is_above_average:
            count_above_average += 1

    return count_above_average

sample_transactions_q4 = {'T1': 100, 'T2': 200, 'T3': 300}
sample_result_q4 = count_transactions_above_average(sample_transactions_q4)
print("count_transactions_above_average:", sample_result_q4)


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
    price_points = list(prices.items())
    daily_returns = {}

    if len(price_points) <= 1:
        return daily_returns

    previous_date, previous_price = price_points[0]

    for index in range(1, len(price_points)):
        current_date, current_price = price_points[index]

        if previous_price == 0:
            percentage_change = 0.0
        else:
            price_difference = current_price - previous_price
            raw_change = price_difference / previous_price
            percentage_change = raw_change * 100

        rounded_change = round(percentage_change, 2)
        daily_returns[current_date] = rounded_change

        previous_date = current_date
        previous_price = current_price

    return daily_returns

sample_prices_q5 = {
    '2023-02-01': 200.0,
    '2023-02-02': 220.0,
    '2023-02-03': 210.0,
}
sample_result_q5 = calculate_daily_returns(sample_prices_q5)
print("calculate_daily_returns:", sample_result_q5)


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
    merged_portfolio = {}

    for ticker, quantity in portfolio1.items():
        merged_portfolio[ticker] = quantity

    for ticker, quantity in portfolio2.items():
        existing_quantity = merged_portfolio.get(ticker, 0)
        merged_portfolio[ticker] = existing_quantity + quantity

    return merged_portfolio

sample_portfolio_q6_one = {'AAPL': 50}
sample_portfolio_q6_two = {'AAPL': 30, 'MSFT': 100}
sample_result_q6 = merge_portfolios(sample_portfolio_q6_one, sample_portfolio_q6_two)
print("merge_portfolios:", sample_result_q6)


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
    increase_factor = 1 + (percentage / 100)
    increased_portfolio = {}

    for ticker, price in portfolio.items():
        increased_price = price * increase_factor
        rounded_price = round(increased_price, 2)
        increased_portfolio[ticker] = rounded_price

    return increased_portfolio

sample_portfolio_q7 = {'MSFT': 50.0, 'GOOG': 200.0}
sample_percentage_q7 = 5.0
sample_result_q7 = apply_percentage_increase(sample_portfolio_q7, sample_percentage_q7)
print("apply_percentage_increase:", sample_result_q7)


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
        is_first_entry = max_quantity is None
        is_new_max = quantity > max_quantity if max_quantity is not None else False

        if is_first_entry or is_new_max:
            max_ticker = ticker
            max_quantity = quantity

    return max_ticker

sample_portfolio_q8 = {'A': 500, 'B': 700}
sample_result_q8 = find_max_holding(sample_portfolio_q8)
print("find_max_holding:", sample_result_q8)
