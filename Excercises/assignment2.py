# Assignment 2
#
# Create the functions below EXACTLY as specified.
# ⚠️ AUTO-GRADER CRITICAL WARNING ⚠️
# - Changing function names/parameters will cause 50% score deduction
# - Incorrect return types/formats will result in 0 marks for that question
# - Comments are ignored by Python and auto-grader (you can add your own)



# Question 1 (25 points)
# Function Name: count_monthly_transactions
# Input Parameters:
#   - transactions (list of dictionaries, each with "year" (integer) and "month" (integer))
#
# Expected Return Value:
#   - A dictionary where keys are strings in "YYYY-MM" format, and values are the total number of transactions 
#     in that month (integer).
#
# Example 1:
#   count_monthly_transactions([
#     {"year": 2023, "month": 10},  
#     {"year": 2023, "month": 10},  
#     {"year": 2024, "month": 1}  
#   ]) 
# Result:
#   {"2023-10": 2, "2024-01": 1}  
def count_monthly_transactions(transactions):  
    monthly_counts = {}  # maps "YYYY-MM" -> number of transactions in that month

    for transaction in transactions:
        year = transaction.get("year")
        month = transaction.get("month")

        # Ensure month is always two digits (e.g., "03" for March)
        key = f"{year:04d}-{month:02d}"
        monthly_counts[key] = monthly_counts.get(key, 0) + 1

    return monthly_counts  

# Quick check for Question 1
print("Q1 count_monthly_transactions example:")
q1_transactions_example = [
    {"year": 2023, "month": 10},
    {"year": 2023, "month": 10},
    {"year": 2024, "month": 1},
]
print(count_monthly_transactions(q1_transactions_example))



# Question 2 (25 points)
# Function Name: check_daily_spending
# Input Parameters:
#   - transactions (list of dictionaries, each with "date" (string in "YYYY-MM-DD" format) and "amount" (float))
#   - daily_limit (float)
#
# Expected Return Value:
#   - A sorted list of dates (strings) where the total transaction amount for the day exceeds daily_limit.
#
# Examples 1:
#   check_daily_spending([
#     {"date": "2023-10-09", "amount": 150.0},  
#     {"date": "2023-10-10", "amount": 150.0},  
#     {"date": "2023-10-10", "amount": 60.0},  
#     {"date": "2023-10-11", "amount": 200.0}  
#   ], 200.0) 
# Result:
#   ["2023-10-10"]  

def check_daily_spending(transactions, daily_limit):  
    totals_by_date = {}  # maps date string -> total spent on that date

    for transaction in transactions:
        date = transaction.get("date")
        amount = transaction.get("amount", 0.0)
        totals_by_date[date] = totals_by_date.get(date, 0.0) + amount

    # Collect dates where the daily total exceeds the allowed limit
    over_limit_dates = [
        date for date, total in totals_by_date.items() if total > daily_limit
    ]

    return sorted(over_limit_dates)  

# Quick check for Question 2
print("\nQ2 check_daily_spending example:")
q2_transactions_example = [
    {"date": "2023-10-09", "amount": 150.0},
    {"date": "2023-10-10", "amount": 150.0},
    {"date": "2023-10-10", "amount": 60.0},
    {"date": "2023-10-11", "amount": 200.0},
]
print(check_daily_spending(q2_transactions_example, 200.0))



# Question 3 (30 points)
# Function Name: split_installments
# Input Parameters:
#   - amount (float, total amount to split)
#   - num_installments (integer, ≥1)
#
# Expected Return Value:
#   - A list of floats representing equal installments. The sum must equal amount, rounded to two decimal places. 
#     Distribute any remainder across the first installments. (This part is tricky)
#
# Example 1:
#   split_installments(100.0, 3) 
# Result:
#   [33.34, 33.33, 33.33]  
#
# Example 2:
#   split_installments(50.01, 2) 
# Result:
#   [25.01, 25.00]  
#
# Example 3:
#   split_installments(100.0, 4) 
# Result:
#   [25.0, 25.0, 25.0, 25.0]  

def split_installments(amount, num_installments):  
    if num_installments <= 0:
        return []

    # Work in whole cents to avoid floating-point rounding surprises.
    total_cents = round(amount * 100)
    base_installment = total_cents // num_installments
    remainder = total_cents % num_installments  # cents that still need to be distributed

    installments = []
    for index in range(num_installments):
        # Spread the remainder by adding one extra cent to the earliest installments
        cents_for_this_payment = base_installment + (1 if index < remainder else 0)
        installments.append(round(cents_for_this_payment / 100.0, 2))

    return installments  

# Quick check for Question 3
print("\nQ3 split_installments examples:")
print(split_installments(100.0, 3))
print(split_installments(50.01, 2))
print(split_installments(100.0, 4))




# Question 4 (20 points) 
# CHALLENGING QUESTION
#
# Function Name: merge_portfolios
# Input Parameters:
#   - portfolio1 (dictionary: keys are stock symbols (string), values are dictionaries with keys "quantity" (integer) 
#     and "average_price" (float))
#   - portfolio2 (dictionary: same structure as portfolio1)
#
# Expected Return Value:
#   - A merged dictionary where each stock’s quantity is the sum of its quantities in both portfolios, and the average 
#     price is the weighted average of the two portfolios. Stocks in only one portfolio retain their original quantity 
#     and average price. The average price should be rounded to two decimal places.
#
# Examples 1:
#   merge_portfolios({"AAPL": {"quantity": 50, "average_price": 100.0}, 
#                     "TSLA": {"quantity": 10, "average_price": 200.0}}, 
#                    {"AAPL": {"quantity": 30, "average_price": 110.0}, 
#                     "GOOG": {"quantity": 5, "average_price": 300.0}}) 
# Result:
#   {"AAPL": {"quantity": 80, "average_price": 103.75}, 
#    "TSLA": {"quantity": 10, "average_price": 200.0}, 
#    "GOOG": {"quantity": 5, "average_price": 300.0}}
#
#
# Example 2:    
#   merge_portfolios({"MSFT": {"quantity": 20, "average_price": 150.0}, 
#                     "AMZN": {"quantity": 15, "average_price": 250.0}}, 
#                    {"MSFT": {"quantity": 10, "average_price": 160.0}, 
#                     "META": {"quantity": 8, "average_price": 220.0}}) 
# Result:
#   {"MSFT": {"quantity": 30, "average_price": 153.33}, 
#    "AMZN": {"quantity": 15, "average_price": 250.0}, 
#    "META": {"quantity": 8, "average_price": 220.0}}
#
#
# Example 3:
#   merge_portfolios({"IBM": {"quantity": 40, "average_price": 120.0}, 
#                     "ORCL": {"quantity": 25, "average_price": 180.0}}, 
#                    {"IBM": {"quantity": 20, "average_price": 130.0}, 
#                     "CSCO": {"quantity": 12, "average_price": 200.0}}) 
# Result:
#   {"IBM": {"quantity": 60, "average_price": 123.33}, 
#    "ORCL": {"quantity": 25, "average_price": 180.0}, 
#    "CSCO": {"quantity": 12, "average_price": 200.0}}
# 

def merge_portfolios(portfolio1, portfolio2):  
    merged = {}

    # Consider every stock that appears in either portfolio.
    for symbol in set(portfolio1.keys()).union(portfolio2.keys()):
        p1_info = portfolio1.get(symbol, {"quantity": 0, "average_price": 0.0})
        p2_info = portfolio2.get(symbol, {"quantity": 0, "average_price": 0.0})

        quantity1 = p1_info.get("quantity", 0)
        price1 = p1_info.get("average_price", 0.0)
        quantity2 = p2_info.get("quantity", 0)
        price2 = p2_info.get("average_price", 0.0)

        total_quantity = quantity1 + quantity2

        if total_quantity == 0:
            # Should not happen with valid inputs, but keeps the logic safe.
            merged_price = 0.0
        elif quantity1 == 0:
            merged_price = price2
        elif quantity2 == 0:
            merged_price = price1
        else:
            weighted_total = (quantity1 * price1) + (quantity2 * price2)
            merged_price = weighted_total / total_quantity

        merged[symbol] = {
            "quantity": total_quantity,
            "average_price": round(merged_price, 2),
        }

    return merged  

# Quick check for Question 4
print("\nQ4 merge_portfolios examples:")

# Example 1
portfolio1_ex1 = {
    "AAPL": {"quantity": 50, "average_price": 100.0},
    "TSLA": {"quantity": 10, "average_price": 200.0},
}
portfolio2_ex1 = {
    "AAPL": {"quantity": 30, "average_price": 110.0},
    "GOOG": {"quantity": 5, "average_price": 300.0},
}
print(merge_portfolios(portfolio1_ex1, portfolio2_ex1))

# Example 2
portfolio1_ex2 = {
    "MSFT": {"quantity": 20, "average_price": 150.0},
    "AMZN": {"quantity": 15, "average_price": 250.0},
}
portfolio2_ex2 = {
    "MSFT": {"quantity": 10, "average_price": 160.0},
    "META": {"quantity": 8, "average_price": 220.0},
}
print(merge_portfolios(portfolio1_ex2, portfolio2_ex2))

# Example 3
portfolio1_ex3 = {
    "IBM": {"quantity": 40, "average_price": 120.0},
    "ORCL": {"quantity": 25, "average_price": 180.0},
}
portfolio2_ex3 = {
    "IBM": {"quantity": 20, "average_price": 130.0},
    "CSCO": {"quantity": 12, "average_price": 200.0},
}
print(merge_portfolios(portfolio1_ex3, portfolio2_ex3))
