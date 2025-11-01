# BMI = Weight / Height^2    kg and m

def convert_to_m(height):
    return height/100


def calculate_bmi(height, weight):
    #print(weight)
    #print(height)
    return weight/height**2


def bmi_test(bmi):
    print('Your bmi is {}'.format(round(bmi, 2)))
    if bmi < 18.5:
        print('You\'d better eat more!')
    elif bmi < 25:
        print('Good job!')
    elif bmi < 30:
        print('You\'d better do some exercises')
    else:
        print('You\'d better consult doctor')


def bmi_app():
    try:
        age = int(input('What\'s your age?'))
    except ValueError:
        print("You need to enter 0 - 100 as your age")
        try:
            age = int(input('What\'s your age?'))
        except:
            print("Your input is still wrong. Quitting the app")
            return

    if age < 18:
        print("Sorry I can't help you.")
    else:
        height = float(input('What\'s your height (in cm)? '))
        height = convert_to_m(height)
        weight = float(input('what\'s your weight (in kg) '))
        bmi = calculate_bmi(height, weight)
        bmi_test(bmi)

    print('-------------------------------------------')
    bmi_app()


bmi_app()

# how to improve?
# Q1 what if the weight is not integer? e.g. 62.5