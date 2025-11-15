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
    pass  



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
    pass  



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
    pass  




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
    pass  

