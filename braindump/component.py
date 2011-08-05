import collections
import contextlib
import thread


def predicate(function):
    class _Predicate:
        class __metaclass__(type):
            def __instancecheck__(self, instance):
                return function(instance)
    return _Predicate


def require(**annotations):
    def decorator(function):
        if not hasattr(function, '__annotations__'):
            function.__annotations__ = {}
        function.__annotations__.update(annotations)
        return function
    return decorator


Identity = collections.namedtuple('Identity', ['id', 'hash', 'context'])


class Registry(object):

    def __init__(self):
        self._objects = {}
        self._stacked = collections.OrderedDict()
        self._tagged = {}
        self.tag('registry', self)

    def context(self):
        return thread.get_ident()

    def identify(self, object):
        if isinstance(object, collections.Hashable):
            return Identity(None, hash(object), None)
        return Identity(id(object), None, self.context())

    def add(self, object):
        self._objects[self.identify(object)] = object

    @contextlib.contextmanager
    def stack(self, object):
        identity = self.identify(object)
        self._stacked[identity] = object
        try:
            yield object
        finally:
            del self._stacked[identity]

    def tag(self, tag, object):
        self._tagged[tag] = object

    def __getitem__(self, type):
        if type in self._tagged:
            yield self._tagged[type]
            return
        for identity in reversed(self._stacked):
            if identity.context is not None != self.context():
                continue
            object = self._stacked[identity]
            if isinstance(object, type):
                yield object
                break
        else:
            for object in self._objects.itervalues():
                if isinstance(object, type):
                    yield object