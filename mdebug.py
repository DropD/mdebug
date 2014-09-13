import traceback, re, os
from analyzer import analyzer_interface
'''
Debugging utility module.

classes:
    mdebug      - debugger class, extracts debug info and passes it to an analyzer if given,
                  or an instance of no_analyzer otherwise.
    no_analyzer - minimal implementation of the analyzer interface (does nothing).

interfaces:
    analyzer:
        The analyzer is passed the source code of the expression to be debugged and is then
        prompted to display the results. It must implement the following two methods:

        methods:
            * analyze_source(self, source_code)
            * display_analysis(self)
'''

class no_analyzer(analyzer_interface):
    '''
    Minimal implementation of the analyzer interface. Performs no analysis.
    '''
    def analyze_source(self, code):
        pass
    def display_analysis(self):
        pass

class mdebug(object):
    '''
    Debugging class.
    usage: 
        DBG = mdebug()
        DBG( 1 + 1 )
        
    subclass and override the following functions to customize behaviour:
        mdebug.debug_message(..)
        mdebug.print_debug_info(..)
    look at the respective doc strings to find out more
    '''
    def __init__(self, verbose = True, **kwargs):
        '''
        Construct the debugger object
        args:
            verbose     - print message when starting to debug a file and makes debug messages appear indented under it. (useful for large import trees)
        kwargs (optional):
            analyzer    - an analyzer object (must implement the analyzer interface).
        '''
        self._f = traceback.extract_stack()[-2][0] # extract the file name the instance lives in
        self._verbose = verbose
        self._message_prefix = 'mdebug:'
        if verbose:
            print '{}\tdebugging file {}'.format(self._message_prefix, self._f)
        if 'analyzer' in kwargs:
            self._analyzer = kwargs['analyzer']
        else:
            self._analyzer = no_analyzer()

    def __call__(self, expr, *args, **kwargs):
        '''
        Get info about the function call and use that to extract and display debug information.
        kwargs:
            analyzer    - an analyzer object (must implement the analyzer interface).
        '''
        call_string = traceback.extract_stack()[-2][3] # get the calling source code as string
        args_string = re.sub(r'\A.*?\((.*?)\)$', r'\1', call_string) # extract function arguments
        expr_string = args_string.split(',')[0].strip() # get the first one
        filename, lineno, func = traceback.extract_stack()[-2][0:3] # get additional call stack info

        info_dict = dict( # collect all info in a dict
            prefix      = self._message_prefix,
            spc         = '\t\t' if self._verbose else ' ',
            expr_string = expr_string, 
            expr_value  = expr, 
            file_name   = os.path.split(filename)[1],
            func_name   = func,
            in_func     = ' in {}(...)'.format(func) if func != '<module>' else '',
            line_number = lineno
        ) 

        self.print_debug_info(info_dict) # print debug message

        if 'analyzer' in kwargs:    # check for analyzer given in the debug call
            analyzer = kwargs['analyzer']
        else:                       # analyzer given in constructor or default (mdebug.no_analyzer)
            analyzer = self._analyzer
        analyzer.analyze_source(expr_string)    # run analysis
        analyzer.display_analysis()             # display results

    def debug_message(self):
        '''
        Returns an unformatted python template string for basic debug information. 
        Override to customize the output format.
        Usable fields:
            * prefix        - this will be at the start of every message, default: "mdebug:"
            * spc           - "\t\t" if mdebug.verbose is True, " " otherwise.
            * expr_string   - a string containing the debug expression (exactly) as written in the call.
            * expr_value    - the value of the debug expression.
            * file_name     - the name of the file from where the debugger was called.
            * func_name     - the name of the function calling the debugger's __call__.
            * in_func       - either ' <func_name>(..)' or '' if the calling code was toplevel.
            * line_number   - the line number on which the debugger was called.
        Override print_debug_info(..) to add fields.
        '''
        message = '{prefix}{spc}{expr_string} evaluates to {expr_value}\t<- in {file_name}{in_func} on line {line_number}'
        return message

    def print_debug_info(self, info_dict):
        '''
        Formats and prints the template string returned by mdebug.debug_message()
        Override or extend to:
            * add / change fields to use in the debug_message() of your subclass
            * grab the basic debug info to do something else with it
        '''
        print self.debug_message().format(**info_dict)
