# Class Exercise 5: While Looping
# Create the functions below EXACTLY as specified.
# AUTO-GRADER CRITICAL WARNING
# - Changing function names/parameters will cause 50% score deduction
# - Incorrect return types/formats will result in 0 marks for that question
# - Comments are ignored by Python and auto-grader (you can add your own)

# Use WHILE Loop ONLY for all questions

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
# Professor reference solution using a for loop for comparison
def exclude_tickers_for_loop_example(tickers):
    """Professor's original approach using a for loop."""
    filtered_tickers = []

    for current_ticker in tickers:
        ticker_is_excluded = current_ticker in ['MSFT', 'AAPL', 'GOOGL']
        if not ticker_is_excluded:
            filtered_tickers.append(current_ticker)

    return filtered_tickers

sample_tickers_for_loop_example = ['MSFT', 'TSLA', 'AAPL']
sample_result_for_loop_example = exclude_tickers_for_loop_example(sample_tickers_for_loop_example)
print('exclude_tickers (for loop example):', sample_result_for_loop_example)

def exclude_tickers(tickers):
    """Return every ticker except the three excluded symbols."""
    filtered_tickers = []
    excluded_symbols = ['MSFT', 'AAPL', 'GOOGL']
    current_index = 0

    while current_index < len(tickers):
        current_ticker = tickers[current_index]
        ticker_is_excluded = current_ticker in excluded_symbols

        if not ticker_is_excluded:
            filtered_tickers.append(current_ticker)

        current_index += 1

    return filtered_tickers

sample_tickers_q1 = ['MSFT', 'TSLA', 'AAPL']
sample_result_q1 = exclude_tickers(sample_tickers_q1)
print('exclude_tickers:', sample_result_q1)


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
    """Remove every ticker that appears in the provided blacklist."""
    filtered_tickers = []
    current_index = 0

    while current_index < len(tickers):
        current_ticker = tickers[current_index]
        ticker_is_blacklisted = current_ticker in blacklisted

        if not ticker_is_blacklisted:
            filtered_tickers.append(current_ticker)

        current_index += 1

    return filtered_tickers

sample_tickers_q2 = ['AAPL', 'TSLA', 'GOOGL']
sample_blacklist_q2 = ['AAPL', 'GOOGL']
sample_result_q2 = exclude_blacklisted_tickers(sample_tickers_q2, sample_blacklist_q2)
print('exclude_blacklisted_tickers:', sample_result_q2)


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
def create_10_multiples_list(n):
    """Build a list containing the first n multiples of ten."""
    multiples_of_ten = []
    current_multiplier = 1

    while current_multiplier <= n:
        current_multiple = current_multiplier * 10
        multiples_of_ten.append(current_multiple)
        current_multiplier += 1

    return multiples_of_ten

sample_multiplier_q3 = 3
sample_result_q3 = create_10_multiples_list(sample_multiplier_q3)
print('create_10_multiples_list:', sample_result_q3)


# Question 4
# Function Name: count_income_above_threshold
# Input Parameters:
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
def count_income_above_threshold(incomes):
    """Count how many income values are strictly greater than 1000."""
    threshold_value = 1000
    number_of_months_above_threshold = 0
    current_index = 0

    while current_index < len(incomes):
        current_income = incomes[current_index]
        income_is_above_threshold = current_income > threshold_value

        if income_is_above_threshold:
            number_of_months_above_threshold += 1

        current_index += 1

    return number_of_months_above_threshold

sample_incomes_q4 = [1200.0, 800.0, 1500.0]
sample_result_q4 = count_income_above_threshold(sample_incomes_q4)
print('count_income_above_threshold:', sample_result_q4)


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
def sum_income_above_threshold(incomes):
    """Return the total income from entries greater than 1000."""
    threshold_value = 1000
    total_income_above_threshold = 0.0
    current_index = 0

    while current_index < len(incomes):
        current_income = incomes[current_index]
        income_is_above_threshold = current_income > threshold_value

        if income_is_above_threshold:
            total_income_above_threshold += current_income

        current_index += 1

    return float(total_income_above_threshold)

sample_incomes_q5 = [1200.0, 800.0, 1500.0]
sample_result_q5 = sum_income_above_threshold(sample_incomes_q5)
print('sum_income_above_threshold:', sample_result_q5)


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
def count_items_above_average(numbers):
    """Count how many items are strictly greater than the list average."""
    if len(numbers) == 0:
        return 0

    total_sum = 0.0
    current_index = 0

    while current_index < len(numbers):
        current_value = numbers[current_index]
        total_sum += current_value
        current_index += 1

    number_of_items = len(numbers)
    average_value = total_sum / number_of_items

    count_above_average = 0
    current_index = 0

    while current_index < number_of_items:
        current_value = numbers[current_index]
        value_is_above_average = current_value > average_value

        if value_is_above_average:
            count_above_average += 1

        current_index += 1

    return count_above_average

sample_numbers_q6 = [10.0, 20.0, 30.0]
sample_result_q6 = count_items_above_average(sample_numbers_q6)
print('count_items_above_average:', sample_result_q6)


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
def calculate_daily_percentage_return(prices):
    """Return the day-over-day percentage changes rounded to two decimals."""
    percentage_returns = []

    if len(prices) <= 1:
        return percentage_returns

    current_index = 1

    while current_index < len(prices):
        previous_price = prices[current_index - 1]
        current_price = prices[current_index]

        if previous_price == 0:
            raw_percentage_change = 0.0
        else:
            price_difference = current_price - previous_price
            raw_ratio = price_difference / previous_price
            raw_percentage_change = raw_ratio * 100

        rounded_percentage_change = round(raw_percentage_change, 2)
        percentage_returns.append(rounded_percentage_change)
        current_index += 1

    return percentage_returns

sample_prices_q7 = [100.0, 105.0, 110.0]
sample_result_q7 = calculate_daily_percentage_return(sample_prices_q7)
print('calculate_daily_percentage_return:', sample_result_q7)


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
def calculate_monthly_net_income(incomes, expenses):
    """Compute income minus expense for each month in the data provided."""
    net_incomes = []

    length_of_incomes = len(incomes)
    length_of_expenses = len(expenses)

    total_months = length_of_incomes
    if length_of_expenses < total_months:
        total_months = length_of_expenses

    current_index = 0

    while current_index < total_months:
        current_income = incomes[current_index]
        current_expense = expenses[current_index]
        monthly_net_income = current_income - current_expense
        net_incomes.append(monthly_net_income)
        current_index += 1

    return net_incomes

sample_incomes_q8 = [2000.0, 2500.0]
sample_expenses_q8 = [1500.0, 1200.0]
sample_result_q8 = calculate_monthly_net_income(sample_incomes_q8, sample_expenses_q8)
print('calculate_monthly_net_income:', sample_result_q8)
