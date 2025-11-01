# you can download at
# https://goo.gl/WKdcqo

colors = ['red','blue','green']

for color in colors:
    print('I love {}'.format(color))

range(3)

for i in range(3):
    print(i)

for i in range(5):
    print(i)

# break, pass, continue
for i in range(3):
    cmd = input('Enter command: ')
    if cmd == 'break':
        break
    elif cmd == 'pass':
        pass
        print('command is pass')
    elif cmd == 'continue':
        continue
        print('command is continue')

