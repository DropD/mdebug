import ast, re, os, astor
from astor import codegen
from importlib import import_module

class mdebug(object):

    @classmethod
    def new_nodes_for_old(self, old, new, dbg_dbg_on):
        if dbg_dbg_on:
            print '{} : {}, {} -> {}'.format(old.lineno, old.col_offset, old, new)
            print '{} \n\t|\n\tv\n-> {}\n----'.format(ast.dump(old), ast.dump(new))

    class visitor(ast.NodeVisitor):
        def __init__(self):
            super(mdebug.visitor, self).__init__()
            self.funcname = None
            self.options = None
        def visit_Assign(self, node):
            if hasattr(node.value, 'func'):
                fn = node.value.func.id
                if fn == 'mdebug':
                    self.funcname = node.targets[0].id
                    self.options  = node.value.args
            super(mdebug.visitor, self).generic_visit(node)

    class transformer(ast.NodeTransformer):
        def __init__(self, funcname = 'DEBUG', is_main = False, dbg_dbg = False):
            super(mdebug.transformer, self).__init__()
            self._fn = funcname
            self._db = dbg_dbg
            self.name = '__main__' if is_main else '__module__'

        def visit_Assign(self, node):
            if hasattr(node.value, 'func'):
                fn = node.value.func.id
                if fn == 'mdebug':
                    name_to_main = ast.Assign(
                        targets = [ast.Name(id = '__name__', ctx = ast.Store())],
                        value = ast.Str(s = self.name)
                    )
                    mdebug.new_nodes_for_old(node, name_to_main, self._db)
                    return ast.fix_missing_locations(ast.copy_location(name_to_main, node))
            super(mdebug.transformer, self).generic_visit(node)
            return node

        def make_debug_node(self, call):
            expr_string = re.sub(r'\A[(](.*?)[)]\Z', r'\1', codegen.to_source(call.args[0]))
            debug_string = 'mdebug: {0} evaluates to {1}'

            #~ evalnode  = ast.Call(
                #~ func = ast.Name(id = 'eval', ctx = ast.Load()),
                #~ args = [ast.Str(s  = expr_string)],
                #~ keywords = [],
                #~ starargs = None,
                #~ kwargs = None
            #~ )

            formatnode = ast.Call(
                func = ast.Attribute(
                    value = ast.Str(s = debug_string),
                    attr  = 'format',
                    ctx   = ast.Load()),
                args = [ast.Str(s = expr_string), call.args[0]],
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

        def call_is_debug(self, call):
            if hasattr(call.func, 'id') and call.func.id == self._fn:       # it's a function call
                return True
            elif hasattr(call.func, 'attr') and call.func.attr == self._fn: # it's a method call
                return True
            else:
                return False

        def visit_Call(self, node):
            is_debug_call = self.call_is_debug(node)
            if is_debug_call:
                newnode = ast.copy_location(self.make_debug_node(node), node)
                ast.fix_missing_locations(newnode)
                mdebug.new_nodes_for_old(node, newnode, self._db)
                return newnode
            else:
                super(mdebug.transformer, self).generic_visit(node)
                return node

        def visit_Expr(self, node):
            if hasattr(node.value, 'func') and self.call_is_debug(node.value):
                call = node.value
                if self._db : print 'replaces Expr:'
                newnode = ast.fix_missing_locations(ast.copy_location(self.visit_Call(call), node)) 
                return newnode
            else:
                super(mdebug.transformer, self).generic_visit(node)
                return node

    def __init__(self):
        import __main__ as main
        import sys
        import traceback
        self._filename = traceback.extract_stack()[-2][0]
        #~ self._filename = main.__file__
        #~ if self._filename == main.__file__:
        self._visitor = mdebug.visitor()
        with open(self._filename) as f:
            tree = ast.parse(f.read(), self._filename, 'exec')
            self._visitor.visit(tree)
            if self._visitor.funcname != None:
                is_main = False
                if self._filename == main.__file__:
                    is_main = True
                print 'mdebug: debugging {0}'.format(self._filename)
                if self._visitor.options:
                    dbg_dbg = self._visitor.options[0]
                else:
                    dbg_dbg = False
                self._transformer = mdebug.transformer(self._visitor.funcname, is_main, dbg_dbg)
                self._transformer.visit(tree)
                if self._filename == main.__file__:
                    if dbg_dbg: 
                        print astor.misc.dump(tree)
                        print codegen.to_source(tree)
                        print ''
                cobj = compile(tree, self._filename, 'exec')
                exec(cobj)
                if self._filename == main.__file__:
                    sys.exit()

    def __call__(self, expr):
        print locals()
        pass
