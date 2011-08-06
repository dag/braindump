class Registry(object):

    def __init__(self):
        self._adapters = {}
        self._types = {}

    def __call__(self, object, interface):
        if isinstance(object, interface):
            return object
        for start, stop in self._adapters:
            if stop is interface:
                factory = self[start:stop]
                if isinstance(object, start):
                    return factory(object)
                try:
                    return self(factory(object), interface)
                except TypeError:
                    pass
        raise TypeError('no adaption possible for {0}:{1}'
                        .format(type(object).__name__, interface.__name__))

    def __getitem__(self, spec):
        if isinstance(spec, slice):
            return self._adapters[spec.start, spec.stop]
        else:
            return self._types.get(spec, spec)

    def __setitem__(self, spec, factory):
        if isinstance(spec, slice):
            self._adapters[spec.start, spec.stop] = factory
        else:
            self._types[spec] = factory

    def __delitem__(self, spec):
        if isinstance(spec, slice):
            del self._adapters[spec.start, spec.stop]
        else:
            del self._types[spec]
