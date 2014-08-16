import ast, re, os
from astor import codegen
from importlib import import_module

class mdebug(object):

    class visitor(ast.NodeVisitor):
        #~ def visit_Import(self, node):
            #~ for n in node.names:
                #~ thisfilename = os.path.splitext(os.path.basename(__file__))[0]
                #~ if not n.name == thisfilename:
                    #~ globals()[n.name] = import_module(n.name)
                    #~ if n.asname:
                        #~ globals()[n.asname] = globals()[n.name]
            #~ super(import_visitor, self).generic_visit(node)

        def visit_Assign(self, node):
            if hasattr(node.value, 'func'):
                fn = node.value.func.id
                if fn == 'mdebug':
                    self.funcname = node.targets[0].id
            super(mdebug.visitor, self).generic_visit(node)

    class transformer(ast.NodeTransformer):
        def __init__(self, funcname = 'DEBUG'):
            super(mdebug.transformer, self).__init__()
            self._fn = funcname

        def visit_Assign(self, node):
            if hasattr(node.value, 'func'):
                fn = node.value.func.id
                if fn == 'mdebug':
                    printnode = ast.Pass()
                    return ast.copy_location(printnode, node)
                else:
                    super(mdebug.visitor, self).generic_visit(node)
                    return node
            else:
                super(mdebug.visitor, self).generic_visit(node)
                return node

        def visit_Expr(self, node):
            if hasattr(node.value, 'func'):
                call = node.value
                func = call.func
                if hasattr(func, 'id') and func.id == self._fn:
                    expr_string = re.sub(r'\A[(](.*?)[)]\Z', r'\1', codegen.to_source(call.args[0]))
                    debug_string = 'mdebug: {0} evaluates to {1}'

                    evalnode  = ast.Call(
                        func = ast.Name(id = 'eval', ctx = ast.Load()),
                        args = [ast.Str(s  = expr_string)],
                        keywords = [],
                        starargs = None,
                        kwargs = None
                    )

                    formatnode = ast.Call(
                        func = ast.Attribute(
                            value = ast.Str(s = debug_string),
                            attr  = 'format',
                            ctx   = ast.Load()),
                        args = [ast.Str(s = expr_string), evalnode],
                        keywords = [],
                        starargs = None,
                        kwargs = None
                    )

                    printnode = ast.Print(
                        dest = None, 
                        values = [formatnode], 
                        nl = True
                    )

                    newnode = ast.copy_location(printnode, node)
                    ast.fix_missing_locations(newnode)
                    return newnode

            super(mdebug.transformer, self).generic_visit(node)
            return node

    def __init__(self):
        import __main__ as main
        import sys
        self._filename = main.__file__
        self._visitor = mdebug.visitor()
        print 'mdebug: debugging {0}'.format(self._filename)
        with open(self._filename) as f:
            tree = ast.parse(f.read(), self._filename, 'exec')
            self._visitor.visit(tree)
            self._transformer = mdebug.transformer(self._visitor.funcname)
            self._transformer.visit(tree)
            cobj = compile(tree, self._filename, 'exec')
            exec(cobj)
        sys.exit()

    def __call__(self, expr):
        pass
