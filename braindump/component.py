import collections
import contextlib
import thread


Identity = collections.namedtuple('Identity', ['id', 'hash', 'context'])


class Registry(object):

    def __init__(self):
        self._objects = {}
        self._stacked = collections.OrderedDict()

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

    def __getitem__(self, type):
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
