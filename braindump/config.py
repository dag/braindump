import copy


class Node(object):

    __slots__ = ('__fields',)

    def __init__(self, **fields):
        self.__fields = {}
        for key, value in fields.iteritems():
            if isinstance(value, dict):
                self.__fields[key] = type(self)(**value)
            else:
                self.__fields[key] = value

    def __getattr__(self, field):
        try:
            return self.__fields[field]
        except KeyError:
            raise AttributeError(field)

    def __dir__(self):
        return self.__fields.keys()

    def __iter__(self):
        return iter(self.__fields)

    def __eq__(self, other):
        return (isinstance(other, type(self)) and
                self.__fields == other._Node__fields)

    def __repr__(self):
        fields = ', '.join('{0}={1!r}'.format(*item)
                           for item in sorted(self.__fields.iteritems()))
        return '{0}({1})'.format(type(self).__name__, fields)


def merge(mappings):
    merged = {}
    for mapping in mappings:
        stack = [(merged, mapping)]
        while stack:
            destination, source = stack.pop()
            for key in source:
                value = copy.copy(source[key])
                if key not in destination:
                    destination[key] = value
                    continue
                if all(isinstance(x, dict)
                       for x in [value, destination[key]]):
                    stack.append((destination[key], value))
                    continue
                destination[key] = value
    return merged


class Builder(object):

    def __init__(self):
        self._mappings = []

    def add(self, mapping):
        self._mappings.append(mapping)

    def build(self):
        merged = merge(self._mappings)
        config = Node(**merged)
        return config
