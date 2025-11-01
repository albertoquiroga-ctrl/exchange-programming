# Class Exercise 3: List
# Complete the functions below EXACTLY as specified.
# ⚠️ AUTO-GRADER CRITICAL WARNING ⚠️
# - Changing function names/parameters will cause 50% score deduction
# - Incorrect return types/formats will result in 0 marks for that question
# - Comments are ignored by Python and auto-grader (you can add your own)


# 1. create a list with 5 items of the input parameters
def create_list(num1, num2, num3, num4, num5):
    return [num1, num2, num3, num4, num5]  # replace this with correct logic

# 2. sort the list in accending order
def sort_list(list):
    return sorted(list)  # replace this with correct logic

# 3. find the number of items of the list
def find_length(list):
    return len(list)  # replace this with correct logic

# 4. return sorted union of two list, i.e. a list that contains all elements of both list
#    and sort the result in accending order. keep duplicate values
def union_list(list1, list2):
    return sorted(list1 + list2)  # replace this with correct logic

num1 = int(input("Enter 1st number: "))
num2 = int(input("Enter 2nd number: "))
num3 = int(input("Enter 3rd number: "))
num4 = int(input("Enter 4th number: "))
num5 = int(input("Enter 5th number: "))

my_list = create_list(num1, num2, num3, num4, num5)
print("List:", my_list)
print("Length:", find_length(my_list))
print("Sorted List:", sort_list(my_list))
print("Union List:", union_list([8, 0, 5], my_list))