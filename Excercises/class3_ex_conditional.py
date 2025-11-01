# Class Exercise 3: Conditional Statements
# Complete the functions below EXACTLY as specified.
# ⚠️ AUTO-GRADER CRITICAL WARNING ⚠️
# - Changing function names/parameters will cause 50% score deduction
# - Incorrect return types/formats will result in 0 marks for that question
# - Comments are ignored by Python and auto-grader (you can add your own)


# Q1 - create a function to return True if a number is odd, False if it's even
#
#      It's ok that you Google if you don't know how to determine whether a
#      number is odd or even
#
def is_odd(x):
    # do something here
    return x % 2 != 0  # replace this line with the correct logic


# Q2 - create a function to compare two integer. output the bigger number
#      Don't use the max() function for exercise purpose
def compare(x, y):
    if x > y:
        return x
    else:
        return y  # replace this line with the correct logic


# Q3 - create a function to compare three integer. output the bigger number
#      Don't use the max() function for exercise purpose
def compare_3(x, y, z):
    w = x
    if y > w:
        w = y
    if z > w:
        w = z
    return w  # replace this line with the correct logic


# Q4 - create a function to compare 4 integer. output the bigger number
#      Don't use the max() function for exercise purpose
def compare_4(a, b, c, d):
    w = a
    if b > w:
        w = b
    if c > w:
        w = c
    if d > w:
        w = d
    return w  # replace this line with the correct logic


# Q5 - write a function to check whether a year is a leap year. return True or False
def leap_year(year):
    if year % 400 == 0:
        return True
    elif year % 100 == 0:
        return False
    elif year % 4 == 0:
        return True
    else:
        return False  # replace this line with the correct logic

# Q6 - write a function to input 3 anglers of a triangle and check whether that is a
#      valid triangle. return True or False.
def is_triangle(a, b, c):
    if a > 0 and b > 0 and c > 0 and a + b + c == 180:
        return True
    else:
        return False

x = int(input('test is_odd: '))
print(is_odd(x))

x1 = int(input('test compare: '))
x2 = int(input('test compare: '))
print(compare(x1, x2))

x1 = int(input('test compare_3: '))
x2 = int(input('test compare_3: '))
x3 = int(input('test compare_3: '))
print(compare_3(x1, x2, x3))

x1 = int(input('test compare_4: '))
x2 = int(input('test compare_4: '))
x3 = int(input('test compare_4: '))
x4 = int(input('test compare_4: '))
print(compare_4(x1, x2, x3, x4))

x = int(input('test leap_year: '))
print(leap_year(x))

x1 = int(input('test is_triangle: '))
x2 = int(input('test is_triangle: '))
x3 = int(input('test is_triangle: '))
print(is_triangle(x1, x2, x3))