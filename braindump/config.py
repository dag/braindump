import copy


class Node(object):

    __slots__ = ('__children',)

    def __init__(self, **children):
        self.__children = {}
        for key, value in children.iteritems():
            if isinstance(value, dict):
                self.__children[key] = type(self)(**value)
            else:
                self.__children[key] = value

    def __getattr__(self, name):
        try:
            return self.__children[name]
        except KeyError:
            raise AttributeError(name)

    def __dir__(self):
        return self.__children.keys()

    def __iter__(self):
        return iter(self.__children)

    def __eq__(self, other):
        return (isinstance(other, type(self)) and
                self.__children == other._Node__children)

    def __repr__(self):
        children = ', '.join('{0}={1!r}'.format(*item)
                             for item in sorted(self.__children.iteritems()))
        return '{0}({1})'.format(type(self).__name__, children)


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
