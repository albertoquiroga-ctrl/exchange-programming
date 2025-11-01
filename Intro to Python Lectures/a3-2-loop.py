vocabs = {'programming': ['the activity or job of writing computer programs','_______ming'],
          'python': ['a very large snake that kills animals for food by wrapping itself around them and crushing them', '___hon'],
          'fun': ['pleasure, enjoyment, or entertainment', '__n']}


vocabs.keys()

vocabs.values()

vocabs.items()

for key in vocabs.keys():
    print(key)

for value in vocabs.values():
    print(value)

for key,value in vocabs.items():
    print('{} ({})\n  {}'.format(key,value[1],value[0]))