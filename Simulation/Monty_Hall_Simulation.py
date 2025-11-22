# Suppose you're on a game show, and you're given the choice of three doors:
# Behind one door is a car; behind the others, goats.
#
# You pick a door, say No. 1, and the host, who knows what's behind the doors, opens another door, say No. 3, which has a goat.
# He then says to you, "Do you want to pick door No. 2?" Is it to your advantage to switch your choice?
#
# http://onlinestatbook.com/2/probability/monty_hall_demo.html


import random

def createSetup():
    doors = [False, False, False]
    doors[random.randint(0,2)] = True
    return doors


# Given your initial choice and whether you want to switch
def pick(choice,switch):
    doors = createSetup()
    if doors[choice]:
        if switch:
            return False
        else:
            return True

    else:
        if switch:
            return True
        else:
            return False

# return win rate
def simulation(switch,num_trial):
    win_count = 0
    for i in range(num_trial):
        if pick(random.randint(0,2),switch):
            win_count += 1
    return win_count/num_trial

print("Probability of Switching     {}".format(simulation(True, 100000)))
print("Probability of Not Switching {}".format(simulation(False, 100000)))