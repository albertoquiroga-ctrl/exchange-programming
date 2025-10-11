def cal_formula(x, y):
    try:
        return (x - 1) / (y - 1)
    except ZeroDivisionError:
        return 0


print(cal_formula(11, 6))  # expected 2.0
print(cal_formula(8, 1))   # expected 0 because of division by zero
print(cal_formula(5, 2))   # expected 2.0
