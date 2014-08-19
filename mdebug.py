import ast, re, os
from astor import codegen
from importlib import import_module

class mdebug(object):

    class visitor(ast.NodeVisitor):
        def __init__(self):
            super(mdebug.visitor, self).__init__()
            self.funcname = None
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
                    name_to_main = ast.Assign(
                        targets = [ast.Name(id = '__name__', ctx = ast.Store())],
                        value = ast.Str(s = '__main__')
                    )
                    return ast.fix_missing_locations(ast.copy_location(name_to_main, node))
            super(mdebug.transformer, self).generic_visit(node)
            return node

        def make_debug_node(self, call):
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
            return printnode

        def visit_Call(self, node):
            is_debug_call = False
            if hasattr(node.func, 'id') and node.func.id == self._fn:       # it's a function call
                is_debug_call = True
            elif hasattr(node.func, 'attr') and node.func.attr == self._fn: # it's a method call
                is_debug_call = True
            if is_debug_call:
                newnode = ast.copy_location(self.make_debug_node(node), node)
                ast.fix_missing_locations(newnode)
                return newnode
            else:
                super(mdebug.transformer, self).generic_visit(node)
                return node

        def visit_Expr(self, node):
            if hasattr(node.value, 'func'):
                call = node.value
                return self.visit_Call(call)

            super(mdebug.transformer, self).generic_visit(node)
            return node

    def __init__(self):
        import __main__ as main
        import sys
        import traceback
        self._filename = traceback.extract_stack()[-2][0]
        #~ self._filename = main.__file__
        if self._filename == main.__file__:
            self._visitor = mdebug.visitor()
            with open(self._filename) as f:
                tree = ast.parse(f.read(), self._filename, 'exec')
                self._visitor.visit(tree)
                if self._visitor.funcname != None:
                    print 'mdebug: debugging {0}'.format(self._filename)
                    self._transformer = mdebug.transformer(self._visitor.funcname)
                    self._transformer.visit(tree)
                    cobj = compile(tree, self._filename, 'exec')
                    exec(cobj)
                    sys.exit()

    def __call__(self, expr):
        pass
