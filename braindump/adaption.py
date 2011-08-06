import __builtin__ as builtins


class Registry(object):

    def __init__(self):
        self._adapter_factories = {}
        self._type_factories = {}

    def add(self, factory, from_type, to_type=None):
        if to_type is None:
            to_type = factory
        self._adapter_factories[(to_type, from_type)] = factory

    def __call__(self, object, type):
        if isinstance(object, type):
            return object
        for to_type, from_type in self._adapter_factories:
            if to_type is type:
                factory = self._adapter_factories[(to_type, from_type)]
                if isinstance(object, from_type):
                    return factory(object)
                try:
                    return self(factory(object), type)
                except TypeError:
                    pass
        raise TypeError('no adapter for {0!r} to {1!r}'
                        .format(builtins.type(object), type))

    def __getitem__(self, type):
        try:
            return self._type_factories[type]
        except KeyError:
            return type

    def __setitem__(self, type, factory):
        self._type_factories[type] = factory

    def __delitem__(self, type):
        del self._type_factories[type]
