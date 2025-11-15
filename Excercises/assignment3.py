# Assignment 3
#
# Create the functions below EXACTLY as specified.
# ⚠️ AUTO-GRADER CRITICAL WARNING ⚠️
# - Changing function names/parameters will cause 50% score deduction
# - Incorrect return types/formats will result in 0 marks for that question
# - Comments are ignored by Python and auto-grader (you can add your own)


# Question 1 (50 points)
# Function Name: ib_trading_fee_hk(qty, price)
# 
# Background:
# This function calculates the trading fee for HKD stock trade in Hong Kong 
# through Interactive Brokers using their Tier 1 of tiered fee structure.
# 
# For reference:
# https://www.interactivebrokers.com.hk/en/pricing/commissions-stocks-asia-pacific.php?re=apac
#
# Fee Structure:
#   Commission Tier I - 0.05% of Trade Value (Minimum HKD 18)	
#   Exchange Fee - 0.00565% trade value
#   Clearing Fee - 0.002% trade value (Minimum HKD 2, Maximum HKD 100)
#   SFC Transaction Levy - 0.0027% trade value
#   FRC Transaction Levy - 0.00015% trade value
#   HK Stamp Duty - 0.1% (rounded up to the nearest 1.00 for SEHK stocks)
#
# Input Parameters:
#   - qty (integer): number of shares
#   - price (float): price per share
#
# Expected Return Value:
#   - Total fee in HKD rount to 3 decimal place 
#
# Example 1:
#   ib_trading_fee_hk(1000, 10.0)
# Result:
#   30.85
#
# Example 2:
#   ib_trading_fee_hk(500, 100.0) 
# Result:
#   81.25
#
# Example 3:
#   ib_trading_fee_hk(100, 500.0) 
# Result:
#   81.25
#
# Example 4:
#   ib_trading_fee_hk(10, 10.0) 
# Result:
#   21.009
#
def ib_trading_fee_hk(qty, price):
    pass


# Question 2 (30 points)
# Function Name: has_consecutive_increase
# Input Parameters:
#   - prices (list of floats, representing daily closing prices)
#
# Expected Return Value:
#   - True if there are at least 3 consecutive days where each day’s price is higher than the previous. False otherwise.
#
# Example 1 :
#   has_consecutive_increase([10.0, 11.0, 12.0, 13.0]) 
# Result:
#   True
#
# Example 2:
#   has_consecutive_increase([10.0, 9.0, 10.5, 11.0, 12.0]) 
# Result:
#   True
#
# Example 3:
#   has_consecutive_increase([10.0, 11.0, 10.5, 12.0, 10.0]) 
# Result:
#   False

def has_consecutive_increase(prices):  
    pass  



# Question 3 (20 points)
# This question is very challenging
#
# Function Name: calculate_fifo_gains
# Input Parameters:
#   - transactions (list of dictionaries with "type" ("BUY"/"SELL"), "shares" (integer), "price" (float), "timestamp" (string in ISO format))
#
# Expected Return Value:
#   - A list containing:
#     - Total capital gains (float) after processing all transactions.
#     - A list of dictionaries representing the outstanding shares inventory after all the sells, 
#       each with keys "shares" (integer) and "price" (float).
#
# Background:
#   FIFO (First-In-First-Out) is a method of processing transactions where the first items added to a system are the 
#   first to be removed. In the context of stock trading, this means that the first shares bought are the first to be
#   sold.
#
# Rules:
#   - Sell shares in FIFO order.
#   - There will be NO transactions that would leave you with a negative number of shares.
#   - Gains = sell_price × shares - sum(buy_prices × shares).
#
# Example 1:
#   transactions = [  
#     {"type": "BUY", "shares": 100, "price": 10.0, "timestamp": "2023-01-01"},  
#     {"type": "BUY", "shares": 50, "price": 12.0, "timestamp": "2023-02-01"},  
#     {"type": "SELL", "shares": 80, "price": 15.0, "timestamp": "2023-03-01"}  
#   ]  
#   calculate_fifo_gains(transactions)  
# Result:
#   (400.0, [{"shares": 20, "price": 10.0}, {"shares": 50, "price": 12.0}])  
#
# 
# Example 2:
#   transactions = [
#     {"type": "BUY", "shares": 200, "price": 20.0, "timestamp": "2023-01-01"},
#     {"type": "SELL", "shares": 150, "price": 25.0, "timestamp": "2023-02-01"},
#     {"type": "BUY", "shares": 100, "price": 22.0, "timestamp": "2023-03-01"},
#     {"type": "SELL", "shares": 120, "price": 30.0, "timestamp": "2023-04-01"}
#   ]
#   calculate_fifo_gains(transactions)
#
# Result:
#   (1810.0, [{"shares": 30, "price": 22.0}])
#
# Example 3:
#   transactions = [
#     {"type": "BUY", "shares": 300, "price": 50.0, "timestamp": "2023-01-01"},
#     {"type": "BUY", "shares": 200, "price": 45.0, "timestamp": "2023-02-01"}, 
#     {"type": "SELL", "shares": 400, "price": 55.0, "timestamp": "2023-03-01"},
#     {"type": "SELL", "shares": 50, "price": 40.0, "timestamp": "2023-04-01"}
#   ]
#   calculate_fifo_gains(transactions)
#
# Result:
#   (2250.0, [{"shares": 50, "price": 45.0}])
#

def calculate_fifo_gains(transactions):
    pass