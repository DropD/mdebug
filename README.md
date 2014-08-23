# mdebug

This is a python utility module for expression debugging designed to be similar in use to C/C++ expression debugging macros.

It allows the user to define a function which takes an arbitrary expression to be printed with it's result and additional information.

## Specialities
 * it is not necessary to wrap expressions in quotes.
 * the expression is executed in the context the debug function is called from, no eval calls are used.

## Usage Example:

```python
from mdebug import mdebug

DBG = mdebug()

# your code 1

DBG(1 + 1)

# your code 2
```

will result in the following output:

```
< your code 1 output >
mdebug: 1 + 1 evaluates to 2
< your code 2 output >
```

## How does it work?
mdebug uses the `traceback` module to get info about the source code calling the debug function.

This information is used to format and print the debug message

## Issues:

No known issues.
