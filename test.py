from mdebug import mdebug
import os

DBG = mdebug()

my_path = 'a/b.c'

DBG(os.path.split(my_path))
print('a')
