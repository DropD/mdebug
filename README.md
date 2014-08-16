# mdebug

This is a python utility module for expression debugging designed to be similar in use to C/C++ expression debugging macros.

It allows you to define a function to which you can give an arbitraty python expression, this expression will be printed at runtime together with the result of the expression.
The expression does not have to be escaped with quotes.

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

## Issues:

At the moment mdebug has to be importet and used as

```python
from mdebug import mdebug
<yourname> = mdebug()
```

instanciating with the qualified name does not work yet.
