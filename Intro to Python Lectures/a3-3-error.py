vocabs = {'programming': ['the activity or job of writing computer programs','_______ming'],
          'python': ['a very large snake that kills animals for food by wrapping itself around them and crushing them', '___hon'],
          'fun': ['pleasure, enjoyment, or entertainment', '__n']}


def new_word():
    try:
        word, definition, hint = input('Enter a new word (word|definition|hint): ').split('|')
        print('{} ({})\n   {}'.format(word,hint,definition))
    except ValueError:
        print('Please make sure your format is correct!')
    except:
        print('Something is wrong')

new_word()






def new_word():
    try:
        word, definition, hint = input("Enter a new words (word|definition|hint)").split("|")
        print("{}".format(word))
        print("     - {} ({})".format(definition, hint))
        print('----------------------')
    except ValueError:
        print("Value Error")
        new_word()
    except:
        print("Something is wrong")
        new_word()


def err_example_preventive():
    stock_ticker = ["AAPL", "NVDA", "MSFT", "TSLA"]
    index = input("Enter the Index")
    
    if index.isdigit() and int(index) < len(stock_ticker):
        print(stock_ticker[int(index)])
    else:
        print("Invalid Index")

    err_example_preventive()

def err_example_reactive():
    stock_ticker = ["AAPL", "NVDA", "MSFT", "TSLA"]
    
    try:
        index = int(input("Enter the Index"))
        print(stock_ticker[index])
    except IndexError:
        print("Invalid index")
    except ValueError:
        print("enter integer as index")
    
    err_example_reactive()