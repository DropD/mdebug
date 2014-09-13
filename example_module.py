import mdebug, analyzer
DBG = mdebug.mdebug(analyzer = analyzer.name_analyzer())

DBG('hello {}'.format("world"))

def add(a, b):
    DBG(a + b)
    return a + b
