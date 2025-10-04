# Class Exercise 4: Looping
# Create the functions below EXACTLY as specified.
# ⚠️ AUTO-GRADER CRITICAL WARNING ⚠️
# - Changing function names/parameters will cause 50% score deduction
# - Incorrect return types/formats will result in 0 marks for that question
# - Comments are ignored by Python and auto-grader (you can add your own)


# Question 1
# Function Name: exclude_tickers
# Input Parameters:
#   - tickers (list of stock tickers, type: list of strings)
# Expected Return Value:
#   - A list of stock tickers excluding 'MSFT', 'AAPL', 'GOOGL' (type: list of strings)
#
# Examples:
#   exclude_tickers(['MSFT', 'TSLA', 'AAPL'])
#   > ['TSLA']
#
#   exclude_tickers(['GOOG', 'AMZN', 'NFLX'])
#   > ['GOOG', 'AMZN', 'NFLX']
#
#   exclude_tickers(['AAPL', 'MSFT', 'AMGN'])
#   > ['AMGN']
def exclude_tickers(tickers):
    excluded = {'MSFT', 'AAPL', 'GOOGL'}
    result = []
    for ticker in tickers:
        if ticker not in excluded:
            result.append(ticker)
    return result


# Question 2
# Function Name: exclude_blacklisted_tickers
# Input Parameters:
#   - tickers (list of stock tickers, type: list of strings)
#   - blacklisted (list of stock tickers to exclude, type: list of strings)
# Expected Return Value:
#   - A list of stock tickers excluding all blacklisted tickers (type: list of strings)
#
# Examples:
#   exclude_blacklisted_tickers(['AAPL', 'TSLA', 'GOOGL'], ['AAPL', 'GOOGL'])
#   > ['TSLA']
#
#   exclude_blacklisted_tickers(['MSFT', 'AMZN', 'NFLX'], ['MSFT'])
#   > ['AMZN', 'NFLX']
#
#   exclude_blacklisted_tickers(['IBM', 'GOOGL', 'TSLA'], ['IBM', 'TSLA'])
#   > ['GOOGL']


def exclude_blacklisted_tickers(tickers, blacklisted):
    """Return tickers excluding any symbols in the blacklist."""
    filtered_tickers = []
    for ticker in tickers:
        if ticker not in blacklisted:
            filtered_tickers.append(ticker)
    return filtered_tickers


# Question 3
# Function Name: create_10_multiples_list
# Input Parameters:
#   - n (an integer representing the multiplier, type: int)
# Expected Return Value:
#   - A list of multiples of 10 from 10 to n * 10 (inclusive) (type: list of integers)
#
# Examples:
#   create_10_multiples_list(3)
#   > [10, 20, 30]
#
#   create_10_multiples_list(5)
#   > [10, 20, 30, 40, 50]
#
#   create_10_multiples_list(0)
#   > []


# Question 4
# Function Name: count_income_above_threshold
# nput Parameters:
#   - incomes (list of float numbers representing monthly income, type: list of floats)
# Expected Return Value:
#   - The number of months with income greater than 1000 (type: int)
#
# Examples:
#   count_income_above_threshold([1200.0, 800.0, 1500.0])
#   > 2
#
#   count_income_above_threshold([900.0, 950.0, 1000.0])
#   > 0
#
#   count_income_above_threshold([1100.0, 2000.0, 500.0])
#   > 2


# Question 5
# Function Name: sum_income_above_threshold
# Input Parameters:
#   - incomes (list of float numbers representing monthly income, type: list of floats)
# Expected Return Value:
#   - The sum of all income greater than 1000 (type: float)
#
# Examples:
#   sum_income_above_threshold([1200.0, 800.0, 1500.0])
#   > 2700.0
#
#   sum_income_above_threshold([900.0, 950.0, 1000.0])
#   > 0.0
#
#   sum_income_above_threshold([1100.0, 2000.0, 500.0])
#   > 3100.0


# Question 6
# Function Name: count_items_above_average
# Number of Input Parameters:
#   - numbers (list of float numbers, type: list of floats)
# Expected Return Value:
#   - The number of items above the average of the list (type: int)
# Examples:
#   count_items_above_average([10.0, 20.0, 30.0])
#   > 1
#
#   count_items_above_average([1.0, 2.0, 3.0])
#   > 1
#
#   count_items_above_average([100.0, 200.0, 300.0])
#   > 2

# Question 7
# Function Name: calculate_daily_percentage_return
# Input Parameters:
#   - prices (list of daily stock prices, type: list of floats)
# Expected Return Value:
#   - A list of daily percentage returns rounded to two d.p.(type: list of floats)
#
# Examples:
#   calculate_daily_percentage_return([100.0, 105.0, 110.0])
#   > [5.0, 4.76]
#
#   calculate_daily_percentage_return([200.0, 250.0, 300.0])
#   > [25.0, 20.0]
#
#   calculate_daily_percentage_return([50.0, 50.0, 50.0])
#   > [0.0, 0.0]


# Question 8
# Function Name: calculate_monthly_net_income
# Input Parameters:
#   - incomes (list of float numbers representing monthly income, type: list of floats)
#   - expenses (list of float numbers representing monthly expenses, type: list of floats)
# Expected Return Value:
#   - A list of Monthly Net Income (Income - Expense) (type: list of floats)
#
# Examples:
#   calculate_monthly_net_income([2000.0, 2500.0], [1500.0, 1200.0])
#   > [500.0, 1300.0]
#
#   calculate_monthly_net_income([3000.0, 2800.0], [3000.0, 2800.0])
#   > [0.0, 0.0]
#
#   calculate_monthly_net_income([1000.0], [500.0])
#   > [500.0]