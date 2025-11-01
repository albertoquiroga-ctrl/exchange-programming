# Class Exercise 2: Financial Functions
# Complete the functions below EXACTLY as specified.
# ⚠️ AUTO-GRADER CRITICAL WARNING ⚠️
# - Changing function names/parameters will cause 50% score deduction
# - Incorrect return types/formats will result in 0 marks for that question
# - Comments are ignored by Python and auto-grader (you can add your own)

import math

# Example Solution Format ------------------------------------------------------
# Original question template
def square_area(length):
    # Formula: area = length^2
    # Sample input: 5 → Output: 25
    return 

# What you need to do is to change the function content to be like this:
# You can keep or add comments. But reminder not to change the function name
# and not to change the amount of input parameters.
# You must return the result instead of printing it.
def square_area(length):
    return length ** 2

# Your Tasks -------------------------------------------------------------------
# Question 1 - Calculate circle circumference
def circle_circumference(radius):
    # Formula: 2 * π * radius (use math.pi)
    # Sample input: 3 → Output: ~18.8495559
    # Return type: float
    return 2 * math.pi * radius

print(circle_circumference(3))  # Example usage

# Question 2 - Calculate area of triangle
def triangle_area(base, height):
    # Formula: (base * height) / 2
    # Sample input: 4, 5 → Output: 10.0
    # Return type: float
    return (base * height) / 2
print(triangle_area(4, 5))  # Example usage

# Question 3 - Profit/loss percentage (DECIMAL FORMAT)
def profit_loss_percentage(buy_price, sell_price):
    # Formula: (sell_price - buy_price)/buy_price
    # Return: decimal (NOT percentage), e.g., 3.2% → 0.032
    # Sample input: 100, 103.2 → Output: 0.032
    # Return type: float
    return (sell_price - buy_price) / buy_price
print(profit_loss_percentage(100, 103.2))  # Example usage

# Question 4 - Calculate BMI (height in CENTIMETERS)
def bmi(weight, height):
    # Formula: weight(kg) / (height(m))²
    # Convert height to meters: height/100
    # Sample input: 70, 175 → Output: ~22.857
    # Return type: float
    return weight / ( (height / 100) ** 2 )
print(bmi(70, 175))  # Example usage

# Question 5 - Calculate Simple Interest (rate is DECIMAL)
def simple_interest(principal, rate, year):
    # Formula: principal * rate * year
    # Sample input: 1000, 0.05 (which means 5%), 3 → Output: 150.0
    # Return type: float
    return principal * rate * year
print(simple_interest(1000, 0.05, 3))  # Example usage

# Question 6 - Currency conversion
def convert_currency(amount, exchange_rate):
    # Formula: amount * exchange_rate
    # Sample input: 10000, 0.13 → Output: 1300.0
    # Return type: float
    return amount * exchange_rate
print(convert_currency(10000, 0.13))  # Example usage

# Question 7 - Calculate P/E ratio
def pe_ratio(price_per_share, earnings_per_share):
    # Formula: price_per_share / earnings_per_share
    # Sample input: 150, 7.5 → Output: 20.0
    # Return type: float
    return price_per_share / earnings_per_share
print(pe_ratio(150, 7.5))  # Example usage

# Question 8 - Calculate crypto portfolio value
def crypto_portfolio_value(coin_amount, current_price):
    # Formula: coin_amount * current_price
    # Sample input: 3.5, 28000 → Output: 98000.0
    # Return type: float
    return coin_amount * current_price
print(crypto_portfolio_value(3.5, 28000))  # Example usage