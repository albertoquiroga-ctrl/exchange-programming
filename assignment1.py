# Assignment 1
#
# Create the functions below EXACTLY as specified.
# ⚠️ AUTO-GRADER CRITICAL WARNING ⚠️
# - Changing function names/parameters will cause 50% score deduction
# - Incorrect return types/formats will result in 0 marks for that question
# - Comments are ignored by Python and auto-grader (you can add your own)

# Question 1 (15 points)
# Function Name: days_in_month
#
# Input Parameters:
#   - year (integer)
#   - month (integer, 1-12)
#   - day (integer, included but unused for calculation)
#
# Expected Return Value:
#   - Number of days in the given month (integer), accounting for leap years if the month is February.
#
# DO NOT USE ANY LIBRARY IN THIS QUESTION
#
# Examples:
#   days_in_month(2020, 2, 15) → 29
#   days_in_month(2021, 2, 30) → 28
#   days_in_month(2023, 4, 10) → 30

def days_in_month(year, month, day):
    pass  # Remove this line and implement the function


# Question 2 (15 points)
# Function Name: categorize_expenses
#
# Input Parameters:
#   - transactions (list of dictionaries, each with keys "amount" (float) and "category" (string))
#
#
# Expected Return Value:
#   - A dictionary where keys are categories and values are the total amount spent in each category (float)
#
# Examples:
#   categorize_expenses([{"amount":50.0,"category":"Food"},{"amount":20.0,"category":"Transport"},{"amount":30.0,"category":"Food"}]) → {"Food":80.0,"Transport":20.0}

def categorize_expenses(transactions):
    pass


# Question 3 (20 points)
# Function Name: is_strong_password
#
# Input Parameters:
#   - password (string)
#
# Expected Return Value:
#   - True if the password meets all criteria; False otherwise.
#
#
# Criteria:
#   - At least 8 characters long
#   - Contains at least one uppercase letter
#   - Contains at least one digit
#   - Contains at least one special character (!, @, #, $, %, &)
#
# Examples:
#   is_strong_password("Secure123!") → True
#   is_strong_password("weak") → False
#   is_strong_password("NoSpecial1") → False

def is_strong_password(password):
    pass



# Question 4 (15 points)
# Function Name: identify_low_performers
#
# Input Parameters:
#   - students (dictionary where keys are student names, values are lists of grades)
#   - threshold (integer, minimum average grade)
#
# Expected Return Value:
#   - A sorted list of student names whose average grade is strictly below the threshold
#
# Examples:
#   identify_low_performers({"Alice":[80,75],"Bob":[50,60],"Charlie":[90,85]}, 70) → ["Bob"]

def identify_low_performers(students, threshold):
    pass


# Question 5 (15 points)
# Function Name: validate_transactions
#
# Input Parameters:
#   - transactions (list of dictionaries with "year", "month", "day", "amount" keys)
#
# Expected Return Value:
#   - A dictionary with "valid" and "invalid" keys containing lists of transactions dictionary
#   - A transaction is considered valid if the amount is larger than zero and the date exist
#
# Notes:
#   - You could use days_in_month from Question 1 to validate dates
#   - DO NOT USE ANY LIBRARY IN THIS QUESTION
#
# Examples:
#   validate_transactions([{"year":2023,"month":2,"day":29,"amount":100.0},{"year":2024,"month":2,"day":29,"amount":-50.0}]) → {"valid":[],"invalid":[{"year":2023,"month":2,"day":29,"amount":100.0},{"year":2024,"month":2,"day":29,"amount":-50.0}]}
#   validate_transactions([{"year":2025,"month":3,"day":29,"amount":100.0},{"year":2025,"month":9,"day":29,"amount":-50.0}]) → {"valid":[{"year":2025,"month":3,"day":29,"amount":100.0}],"invalid":[{"year":2025,"month":9,"day":29,"amount":-50.0}]}

def validate_transactions(transactions):
    pass


# Question 6 (20 points)
# Function Name: restock_inventory
#
# Input Parameters:
#   - inventory (dictionary of item:current stock)
#   - min_stock (dictionary of item:minimum required stock)
#
# Expected Return Value:
#   - Dictionary showing additional units needed for each item
#
# Examples:
#   restock_inventory({"Apples":50,"Bananas":20},{"Apples":100,"Bananas":30}) → {"Apples":50,"Bananas":10}

def restock_inventory(inventory, min_stock):
    pass