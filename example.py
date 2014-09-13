import mdebug, example_module
from analyzer import name_analyzer

DBG = mdebug.mdebug(analyzer = name_analyzer())

bla = 5

if __name__ == '__main__':
    DBG(1 + 1)
    example_module.add(1, 1)

    DBG(bla + 8)
