from mdebug import mdebug
import os

DBG = mdebug()

DBG(os.path.split('a/b.c'))
print('a')
