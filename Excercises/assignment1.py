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
    """Return the number of days in the specified month for a given year."""
    # Check that the month value is within the standard calendar range.
    if month < 1 or month > 12:
        return 0

    # Set up the default number of days for each month in a regular year.
    month_lengths = {
        1: 31,
        2: 28,  # February starts at 28 days and may become 29 in a leap year.
        3: 31,
        4: 30,
        5: 31,
        6: 30,
        7: 31,
        8: 31,
        9: 30,
        10: 31,
        11: 30,
        12: 31,
    }

    # Pick the default day count for the provided month.
    days = month_lengths[month]

    # Determine whether the current year should extend February to 29 days.
    if month == 2:
        # A leap year must be divisible by 4.
        divisible_by_four = year % 4 == 0
        # Century years (like 1900) need special handling.
        divisible_by_one_hundred = year % 100 == 0
        # Century years are leap years only if divisible by 400.
        divisible_by_four_hundred = year % 400 == 0

        # Combine the leap year rules into a single decision.
        if divisible_by_four and (not divisible_by_one_hundred or divisible_by_four_hundred):
            days = 29

    # Return the final tally of days for the requested month.
    return days


if __name__ == "__main__":
    # Demonstrate days_in_month with leap year scenarios right after the function definition.
    print("Question 1: days_in_month examples")
    print(" - Days in February 2020:", days_in_month(2020, 2, 15))
    print(" - Days in February 2021:", days_in_month(2021, 2, 15))
    print(" - Days in April 2023:", days_in_month(2023, 4, 10))
    print()


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
    """Return the total spending grouped by category."""
    # Prepare a dictionary that will accumulate totals for each category label.
    totals = {}

    # Process every transaction entry provided in the list.
    for transaction in transactions:
        # Retrieve the category, keeping None if a key is missing.
        category = transaction.get("category")
        # Retrieve the amount while defaulting to 0.0 when absent.
        amount = transaction.get("amount", 0.0)

        # Skip entries that do not specify a category label.
        if category is None:
            continue

        # Ensure the amount participates in numeric addition.
        numeric_amount = float(amount)

        # Initialize the category bucket if we have not seen it yet.
        if category not in totals:
            totals[category] = 0.0

        # Add the current amount to the running total for this category.
        totals[category] += numeric_amount

    # Provide the dictionary that maps each category to its total spend.
    return totals


if __name__ == "__main__":
    # Demonstrate categorize_expenses immediately after its definition.
    print("Question 2: categorize_expenses example")
    categorize_demo_transactions = [
        {"amount": 50.0, "category": "Food"},
        {"amount": 20.0, "category": "Transport"},
        {"amount": 30.0, "category": "Food"},
    ]
    print(" - Categorized expenses:", categorize_expenses(categorize_demo_transactions))
    print()


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
    """Evaluate whether the supplied password satisfies all strength rules."""
    # Verify the password meets the minimum length requirement.
    if len(password) < 8:
        return False

    # Track whether each strength requirement has been fulfilled.
    contains_uppercase = False
    contains_digit = False
    contains_special = False

    # Establish the set of special characters that qualify for the rule.
    allowed_special_characters = set("!@#$%&")

    # Inspect every character in the password individually.
    for character in password:
        # Record the presence of an uppercase letter if encountered.
        if character.isupper():
            contains_uppercase = True

        # Record the presence of a numeric digit if encountered.
        if character.isdigit():
            contains_digit = True

        # Record the presence of an approved special character if encountered.
        if character in allowed_special_characters:
            contains_special = True

    # True only when all required categories have been observed.
    return contains_uppercase and contains_digit and contains_special


if __name__ == "__main__":
    # Demonstrate is_strong_password with valid and invalid examples.
    print("Question 3: is_strong_password examples")
    print(" - Is 'Secure123!' strong?:", is_strong_password("Secure123!"))
    print(" - Is 'weak' strong?:", is_strong_password("weak"))
    print(" - Is 'NoSpecial1' strong?:", is_strong_password("NoSpecial1"))
    print()



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
    """Return a sorted list of student names whose average is below the threshold."""
    # Collect every student that does not meet the required average.
    low_performers = []

    # Check each student's grade history.
    for name, grades in students.items():
        # Handle missing or empty grade lists by treating the average as zero.
        if not grades:
            average_grade = 0
        else:
            # Compute the average grade with explicit numerator and denominator.
            total_points = sum(grades)
            number_of_grades = len(grades)
            average_grade = total_points / number_of_grades

        # Append the student's name when their average falls short of the goal.
        if average_grade < threshold:
            low_performers.append(name)

    # Sort the resulting list alphabetically to produce a stable order.
    return sorted(low_performers)


if __name__ == "__main__":
    # Demonstrate identify_low_performers with three students.
    print("Question 4: identify_low_performers example")
    identify_demo_students = {"Alice": [80, 75], "Bob": [50, 60], "Charlie": [90, 85]}
    print(" - Students below threshold:", identify_low_performers(identify_demo_students, 70))
    print()


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
    """Classify transactions as valid or invalid based on amount and date."""
    # Prepare the resulting structure that separates valid from invalid entries.
    categorized_results = {"valid": [], "invalid": []}

    # Inspect each transaction dictionary in the provided list.
    for transaction in transactions:
        # Pull individual date components and the amount for clarity.
        year = transaction.get("year")
        month = transaction.get("month")
        day = transaction.get("day")
        amount = transaction.get("amount")

        # Confirm that the amount exists, is numeric, and greater than zero.
        amount_is_positive = isinstance(amount, (int, float)) and amount > 0

        # Start by assuming the date is invalid until proven otherwise.
        date_is_valid = False

        # Check that the date fields are all integers before counting days.
        if isinstance(year, int) and isinstance(month, int) and isinstance(day, int):
            # Determine the maximum day value for the provided month and year.
            max_day_for_month = days_in_month(year, month, day)

            # If the month is in range and the day fits between 1 and the maximum, accept the date.
            if max_day_for_month != 0 and 1 <= day <= max_day_for_month:
                date_is_valid = True

        # Choose the destination bucket for the transaction based on the checks above.
        if amount_is_positive and date_is_valid:
            categorized_results["valid"].append(transaction)
        else:
            categorized_results["invalid"].append(transaction)

    # Return the dictionary that separates valid and invalid transactions.
    return categorized_results


if __name__ == "__main__":
    # Demonstrate validate_transactions using valid and invalid entries.
    print("Question 5: validate_transactions example")
    validate_demo_transactions = [
        {"year": 2023, "month": 2, "day": 29, "amount": 100.0},
        {"year": 2024, "month": 2, "day": 29, "amount": -50.0},
        {"year": 2025, "month": 3, "day": 29, "amount": 100.0},
    ]
    print(" - Transaction validation:", validate_transactions(validate_demo_transactions))
    print()


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
    """Determine how many additional units are required for each item."""
    # Initialize a dictionary that will store the restocking requirement per item.
    additional_units_needed = {}

    # Evaluate every item that has a specified minimum requirement.
    for item, required_amount in min_stock.items():
        # Look up the current stock level, assuming zero when the item is absent.
        current_amount = inventory.get(item, 0)

        # Calculate how far the current stock falls short of the required stock.
        shortage = required_amount - current_amount

        # If the item already meets the requirement, record zero instead of a negative number.
        if shortage > 0:
            additional_units_needed[item] = shortage
        else:
            additional_units_needed[item] = 0

    # Provide the mapping from item names to additional units needed.
    return additional_units_needed


if __name__ == "__main__":
    # Demonstrate restock_inventory to highlight shortages.
    print("Question 6: restock_inventory example")
    restock_demo_inventory = {"Apples": 50, "Bananas": 20}
    restock_demo_minimums = {"Apples": 100, "Bananas": 30}
    print(" - Restock requirements:", restock_inventory(restock_demo_inventory, restock_demo_minimums))
