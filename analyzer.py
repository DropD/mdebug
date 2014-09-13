import ast, astor, traceback

class analyzer_interface(object):
    '''
    Analyzer interface, throws NotImplementedError.
    '''
    def __init__(self):
        self._storage = {}
    def analyze_source(self, code):
        raise NotImplementedError()
    def display_analysis(self):
        raise NotImplementedError()
    def store(self, key, value):
        self._storage[key] = value
        return self._storage[key]
    def retrieve(self, key):
        return self._storage[key]

class analyzer_component_visitor(ast.NodeVisitor):
    def __init__(self, parent):
        super(analyzer_component_visitor, self).__init__()
        self._parent = parent

class name_collector_component(analyzer_component_visitor):
    def __init__(self, parent):
        super(name_collector_component, self).__init__(parent)
        self._namelist = set()
    def visit_Name(self, node):
        self._namelist.add(node.id)
    def __call__(self, node):
        self.visit(node)
        self._parent.store('names', self._namelist)

class name_occurrence_component(analyzer_component_visitor):
    def __init__(self, parent):
        super(name_occurrence_component, self).__init__(parent)
    def visit_Name(self, node):
        if node.id in self._namelist:
            self._occurrences[node.id].append((self._filename, node.lineno))

    def analyze_file(self, filename):
        self._namelist = self._parent.retrieve('names')
        self._occurrences = {}
        for name in self._namelist:
            if name not in self._occurrences:
                self._occurrences[name] = []
        self._filename = filename
        try:
            with open(self._filename) as f:
                tree = ast.parse(f.read())
        except Exception as e:
            print type(e)
            print e
        self.visit(tree)
        self._parent.store('name_occurrences', self._occurrences)

class name_analyzer(analyzer_interface):
    '''
    Tracks all names in the expression, displays:
        * other occurences
    '''
    def __init__(self):
        super(name_analyzer, self).__init__()
        self._stack = traceback.extract_stack()[:-1]
        self._collector = name_collector_component(self)
        self._occurrences = name_occurrence_component(self)
        self._filelist = set([fn[0] for fn in self._stack])

    def analyze_source(self, expr_string):
        expr = ast.parse(expr_string)
        self._collector(expr)
        for f in self._filelist:
            self._occurrences.analyze_file(f)

    def display_analysis(self):
        import __main__
        print '--- name_analyzer output ---'
        if len(self._storage['names']) == 0:
            print 'no names found.'
        for name in self._storage['names']:
            print 'found name "{}"'.format(name)
            if name in __main__.__dict__:
                print '\tfound global with value {}'.format(__main__.__dict__[name])
            else:
                print 'no global variable with this name.'
            print '\toccurrences found at'
            for occ in self._storage['name_occurrences'][name]:
                print '\t\tline {occ[1]} in {occ[0]}'.format(occ = occ)
        print '--- end name_analyzer output ---\n'
