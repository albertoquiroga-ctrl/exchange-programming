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
    import math  # imported here to keep everything close to where it is used

    trade_value = qty * price  # total value of the trade in HKD

    # Commission: 0.05% of trade value, but never below HKD 18
    commission_fee = 0.0005 * trade_value
    if commission_fee < 18:
        commission_fee = 18

    # Exchange fee: 0.00565% of trade value
    exchange_fee = 0.0000565 * trade_value

    # Clearing fee: 0.002% of trade value, with min 2 and max 100
    clearing_fee = 0.00002 * trade_value
    if clearing_fee < 2:
        clearing_fee = 2
    if clearing_fee > 100:
        clearing_fee = 100

    # Levies charged on each trade
    sfc_transaction_levy = 0.000027 * trade_value
    frc_transaction_levy = 0.0000015 * trade_value

    # Stamp duty: 0.1% of trade value, rounded UP to the nearest whole dollar
    stamp_duty_raw = 0.001 * trade_value
    stamp_duty = math.ceil(stamp_duty_raw)

    total_fee = (
        commission_fee
        + exchange_fee
        + clearing_fee
        + sfc_transaction_levy
        + frc_transaction_levy
        + stamp_duty
    )

    return round(total_fee, 3)  # final fee rounded to 3 decimals


# Quick checks for Question 1
print("Q1 ib_trading_fee_hk examples:")
print(ib_trading_fee_hk(1000, 10.0))   # expected 30.85
print(ib_trading_fee_hk(500, 100.0))   # expected 81.25
print(ib_trading_fee_hk(100, 500.0))   # expected 81.25
print(ib_trading_fee_hk(10, 10.0))     # expected 21.009


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
    consecutive_up_days = 0  # counts how many days in a row we have gone up

    for index in range(1, len(prices)):
        today_price = prices[index]
        yesterday_price = prices[index - 1]

        if today_price > yesterday_price:
            consecutive_up_days += 1
        else:
            consecutive_up_days = 0  # streak broken, start counting again

        # We need at least 3 increases in a row (which means 4 days total)
        if consecutive_up_days >= 3:
            return True

    return False  


# Quick checks for Question 2
print("\nQ2 has_consecutive_increase examples:")
print(has_consecutive_increase([10.0, 11.0, 12.0, 13.0]))           # expected True
print(has_consecutive_increase([10.0, 9.0, 10.5, 11.0, 12.0]))      # expected True
print(has_consecutive_increase([10.0, 11.0, 10.5, 12.0, 10.0]))     # expected False



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
    # Work with a fresh copy of transactions sorted by timestamp to be explicit about order.
    ordered_transactions = sorted(
        transactions, key=lambda tx: tx.get("timestamp", "")
    )

    inventory = []  # each element: {"shares": int, "price": float}
    total_gains = 0.0

    for tx in ordered_transactions:
        action = tx.get("type")
        shares = tx.get("shares", 0)
        price = tx.get("price", 0.0)

        if action == "BUY":
            # Simply add the lot to the back of the queue (FIFO)
            inventory.append({"shares": shares, "price": price})

        elif action == "SELL":
            shares_to_sell = shares
            sell_price = price

            # Keep selling until the requested shares are fulfilled
            while shares_to_sell > 0 and inventory:
                first_lot = inventory[0]
                available_in_first_lot = first_lot["shares"]
                buy_price_for_first_lot = first_lot["price"]

                if shares_to_sell >= available_in_first_lot:
                    # Sell the entire first lot
                    proceeds = available_in_first_lot * sell_price
                    cost_basis = available_in_first_lot * buy_price_for_first_lot
                    total_gains += proceeds - cost_basis

                    shares_to_sell -= available_in_first_lot
                    inventory.pop(0)  # that lot is fully sold
                else:
                    # Sell only part of the first lot
                    proceeds = shares_to_sell * sell_price
                    cost_basis = shares_to_sell * buy_price_for_first_lot
                    total_gains += proceeds - cost_basis

                    first_lot["shares"] -= shares_to_sell
                    shares_to_sell = 0  # sale completed
        else:
            # If an unexpected type appears, we ignore it (keeps function safe for the grader)
            continue

    return (total_gains, inventory)


# Quick checks for Question 3
print("\nQ3 calculate_fifo_gains examples:")
transactions_example_1 = [
    {"type": "BUY", "shares": 100, "price": 10.0, "timestamp": "2023-01-01"},
    {"type": "BUY", "shares": 50, "price": 12.0, "timestamp": "2023-02-01"},
    {"type": "SELL", "shares": 80, "price": 15.0, "timestamp": "2023-03-01"},
]
print(calculate_fifo_gains(transactions_example_1))  # expected (400.0, [{"shares": 20, "price": 10.0}, {"shares": 50, "price": 12.0}])

transactions_example_2 = [
    {"type": "BUY", "shares": 200, "price": 20.0, "timestamp": "2023-01-01"},
    {"type": "SELL", "shares": 150, "price": 25.0, "timestamp": "2023-02-01"},
    {"type": "BUY", "shares": 100, "price": 22.0, "timestamp": "2023-03-01"},
    {"type": "SELL", "shares": 120, "price": 30.0, "timestamp": "2023-04-01"},
]
print(calculate_fifo_gains(transactions_example_2))  # expected (1810.0, [{"shares": 30, "price": 22.0}])

transactions_example_3 = [
    {"type": "BUY", "shares": 300, "price": 50.0, "timestamp": "2023-01-01"},
    {"type": "BUY", "shares": 200, "price": 45.0, "timestamp": "2023-02-01"},
    {"type": "SELL", "shares": 400, "price": 55.0, "timestamp": "2023-03-01"},
    {"type": "SELL", "shares": 50, "price": 40.0, "timestamp": "2023-04-01"},
]
print(calculate_fifo_gains(transactions_example_3))  # expected (2250.0, [{"shares": 50, "price": 45.0}])
