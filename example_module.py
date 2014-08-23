import mdebug
DBG = mdebug.mdebug()

DBG('hello {}'.format("world"))

def add(a, b):
    DBG(a + b)
    return a + b
