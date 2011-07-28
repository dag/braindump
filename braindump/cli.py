import copy


class ConfigNode(object):

    __slots__ = ('__fields',)

    def __init__(self, **fields):
        self.__fields = fields

    def __getattr__(self, field):
        try:
            return self.__fields[field]
        except KeyError:
            raise AttributeError(field)

    def __dir__(self):
        return self.__fields.keys()

    def __iter__(self):
        return iter(self.__fields)

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
