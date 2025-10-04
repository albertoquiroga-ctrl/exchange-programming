# Class Exercise 4: Library and Random
# Create the functions below EXACTLY as specified.
# AUTO-GRADER CRITICAL WARNING
# - Changing function names/parameters will cause 50% score deduction
# - Incorrect return types/formats will result in 0 marks for that question
# - Comments are ignored by Python and auto-grader (you can add your own)

# Question 1
# Function Name: generate_random_numbers
# Input Parameters:
#   - n (an integer representing the number of random numbers to generate, type: int)
# Expected Return Value:
#   - A list of n random integers between 1 and 100 (type: list of integers)
#
# Examples:
#   generate_random_numbers(5)
#   > [23, 45, 67, 12, 89] (output may vary)
#
#   generate_random_numbers(3)
#   > [90, 15, 73] (output may vary)
#
#   generate_random_numbers(0)
#   > []

import math
import random


def generate_random_numbers(n):
    """Return a list of n random integers between 1 and 100 inclusive."""
    if not isinstance(n, int):
        raise TypeError("n must be an integer")
    if n < 0:
        raise ValueError("n must be non-negative")
    return [random.randint(1, 100) for _ in range(n)]


# Question 2
# Function Name: random_choice
# Input Parameters:
#   - choices (a list of stock tickers to choose from, type: list of strings)
# Expected Return Value:
#   - A randomly selected stock ticker from the list (type: string)
#
# Examples:
#   random_choice(['AAPL', 'GOOGL', 'TSLA'])
#   > 'GOOGL' (output may vary)
#
#   random_choice(['MSFT', 'AMZN', 'NFLX'])
#   > 'MSFT' (output may vary)
#
#   random_choice(['IBM', 'NVDA', 'MSFT'])
#   > 'NVDA' (output may vary)

def random_choice(choices):
    """Return a random choice from the provided list of stock tickers."""
    if not isinstance(choices, list):
        raise TypeError("choices must be provided as a list")
    if not choices:
        raise ValueError("choices must not be empty")
    return random.choice(choices)


# Question 3
# Function Name: import_and_use_math
# Number of Input Parameters:
#   - x (a float number for which to calculate the square root, type: float)
# Expected Return Value:
#   - The square root of x using the math library (type: float)
#
# Examples:
#   import_and_use_math(16.0)
#   > 4.0
#
#   import_and_use_math(25.0)
#   > 5.0
#
#   import_and_use_math(2.0)
#   > 1.4142135623730951

def import_and_use_math(x):
    """Return the square root of x using the math library."""
    if x < 0:
        raise ValueError("x must be non-negative to compute a real square root")
    return math.sqrt(x)


if __name__ == "__main__":
    user_n = int(input("Enter a number: "))
    print(generate_random_numbers(user_n))

    user_choices = input("Enter stock tickers separated by commas: ").split(",")
    user_choices = [choice.strip() for choice in user_choices]
    print(random_choice(user_choices))

    user_x = float(input("Enter a float number: "))
    print(import_and_use_math(user_x))
