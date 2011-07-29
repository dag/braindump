import copy

from . import meta


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

    def __contains__(self, path):
        try:
            self[path]
        except KeyError:
            return False
        return True

    def __getitem__(self, path):
        names = map(meta.string_to_identifier, path.split(u'.'))
        try:
            return reduce(getattr, [self] + names)
        except AttributeError:
            raise KeyError(path)

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


def convert_keys(mapping, converter=meta.string_to_identifier):
    if not isinstance(mapping, dict):
        return mapping
    new = {}
    for key, value in mapping.iteritems():
        new[converter(key)] = convert_keys(value, converter)
    return new


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
        mappings_with_safe_keys = map(convert_keys, self._mappings)
        merged = merge(mappings_with_safe_keys)
        config = Node(**merged)
        return config
