# Non bias Coin Flippling Game
#
# Win Odds = 2.03
# That means if you you bet 10, you will get back 20.3 when you win. i.e. you win 10.3 dollar

def play_game(win_odds, bet_amount):
    import random
    if random.randint(0,1):
        return win_odds * bet_amount
    else:
        return 0






def play_a_strategy(win_odds, starting_capital, bet_percentage, min_bet, num_bet):
    capital = starting_capital
    bet = capital * bet_percentage
    count_bet = 0

    while capital > min_bet and count_bet < num_bet:
        capital -= bet
        payout = play_game(win_odds, bet)

        capital += payout

        bet = capital * bet_percentage
        count_bet += 1

    return capital


def simulation(win_odds, starting_capital, bet_percentage, min_bet, num_bet, num_simulation):
    win_count = 0

    for i in range(num_simulation):
        result = play_a_strategy(win_odds, starting_capital, bet_percentage, min_bet, num_bet)
        if result > starting_capital:
            win_count += 1

    print("Win Rate {}".format(win_count/num_simulation))


simulation(2.1, 1000000, 0.01, 10, 3000, 500)