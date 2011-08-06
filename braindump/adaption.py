import __builtin__ as builtins


class Registry(object):

    def __init__(self):
        self._factories = {}

    def add(self, factory, from_type, to_type=None):
        if to_type is None:
            to_type = factory
        self._factories[(to_type, from_type)] = factory

    def __call__(self, object, type):
        if isinstance(object, type):
            return object
        for to_type, from_type in self._factories:
            if to_type is type:
                factory = self._factories[(to_type, from_type)]
                if isinstance(object, from_type):
                    return factory(object)
                try:
                    return self(factory(object), type)
                except TypeError:
                    pass
        raise TypeError('no adapter for {0!r} to {1!r}'
                        .format(builtins.type(object), type))
