from mdebug import mdebug
import os

DBG = mdebug()

class xy(object):
    def __init__(self, x, y):
        self._x = x
        self._y = y
    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return self.__class__(x, y)
    def __str__(self):
        return '[ {0} {1} ]'.format(self.x, self.y)
    @property
    def x(self):
        return self._x
    @property
    def y(self):
        return self._y

a = xy(1, 1)
b = xy(2, 3)
DBG(a + b)
DBG(a + b == xy(3, 4))

if __name__ == '__main__':
    my_path = 'a/b.c'

    DBG(os.path.split(my_path))
    print('a')
