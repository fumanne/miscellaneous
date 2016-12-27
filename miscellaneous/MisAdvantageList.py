#! -*- coding: utf-8 -*-


class Adlist(list):
    """
    Only support the digital. So support the algorithm
    like: add, mul, floordiv, mod, sub
    """

    def __add__(self, other):
        """
        example: [1,2,3] + [3,4,5] => [4,6,8]
        :param other: other Adlist
        :return: new Adlst
        """
        _new = Adlist()
        if len(self) != len(other):
            raise OverflowError
        for index, data in enumerate(self):
            _new.append(data+other[index])
        return _new

    def __sub__(self, other):
        _new = Adlist()
        if len(self) != len(other):
            raise OverflowError
        for index, data in enumerate(self):
            _new.append(data-other[index])
        return _new

    def __mul__(self, other):
        _new = Adlist()
        if len(self) != len(other):
            raise OverflowError
        for index, data in enumerate(self):
            _new.append(data*other[index])
        return _new

    def __mod__(self, other):
        _new = Adlist()
        if len(self) != len(other):
            raise OverflowError
        for index, data in enumerate(self):
            _new.append(data%other[index])
        return _new

    def __floordiv__(self, other):
        _new = Adlist()
        if len(self) != len(other):
            raise OverflowError
        for index, data in enumerate(self):
            _new.append(data//other[index])
        return _new



x = Adlist()
y = Adlist()
for i in range(1,4):
    x.append(i)

for i in range(10,5, -2):
    y.append(i)

print(x)
print(y)
c1 =  x+y
c2 =  x-y
c3 = y -x
c4 = x * y
c5 = x % y
c6 = x//y
c7 = y//x
print('#'*20)
print(c1)
print(c2)
print(c3)
print(c4)
print(c5)
print(c6)
print(c7)

