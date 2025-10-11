def cal_formula(x: int, y: int):
    """Return (x - 1) / (y - 1), or 0 when the denominator is zero."""
    denominator = y - 1
    if denominator == 0:
        return 0
    return (x - 1) / denominator


print(cal_formula(11, 6))  # example: regular division
print(cal_formula(8, 1))   # example: denominator would be zero
print(cal_formula(5, 2))   # extra: fractional result
