import traceback, re, os

class mdebug(object):
    def __init__(self, verbose = True):
        self._f = traceback.extract_stack()[-2][0] # extract the file name the instance lives in
        self._verbose = verbose
        if verbose:
            print 'mdebug:\tdebugging file {}'.format(self._f)

    def __call__(self, expr, *args, **kwargs):
        call_string = traceback.extract_stack()[-2][3] # get the calling source code as string
        args_string = re.sub(r'\A.*?\((.*?)\)$', r'\1', call_string) # extract function arguments
        expr_string = args_string.split(',')[0].strip() # get the first one
        lineno, func = traceback.extract_stack()[-2][1:3] # get additional call stack info
        print 'mdebug:{spc}{expr_str} evaluates to {expr_value}\t<- in {file_name}{in_func} on line {line}'.format(
            spc = '\t\t' if self._verbose else ' ',
            expr_str = expr_string, 
            expr_value = expr, 
            file_name = os.path.split(self._f)[1],
            in_func = ' in {}(...)'.format(func) if func != '<module>' else '',
            line = lineno
        ) # print debug message
