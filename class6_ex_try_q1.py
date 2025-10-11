def cal_formula(x, y):
    try:
        result = (x + y) / (x - y)
        return result
    except ZeroDivisionError:
        return "Error: Division by zero is not allowed."
    except TypeError:
        return "Error: Invalid input type. Please provide numbers."