import mdebug, example_module

DBG = mdebug.mdebug()

if __name__ == '__main__':
    DBG(1 + 1)
    example_module.add(1, 1)
