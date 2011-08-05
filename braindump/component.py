import collections
import contextlib
import inspect
import itertools
import thread


def predicate(function):
    class _Predicate:
        class __metaclass__(type):
            def __instancecheck__(self, instance):
                return function(instance)
    return _Predicate


def require(*args, **kwargs):
    def decorator(function):
        if not hasattr(function, '__annotations__'):
            function.__annotations__ = {}
        if args:
            kwargs.update(zip(inspect.getargspec(function).args, args))
        function.__annotations__.update(kwargs)
        return function
    return decorator


Identity = collections.namedtuple('Identity', ['id', 'hash', 'context'])


class Registry(object):

    def __init__(self):
        self._objects = {}
        self._stacked = collections.OrderedDict()
        listdict = lambda: collections.defaultdict(list)
        self._tags = collections.defaultdict(listdict)
        self._tags['registry'][None].append(self)

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

    @contextlib.contextmanager
    def tag(self, tag, object):
        context = self.context()
        self._tags[tag][context].append(object)
        try:
            yield object
        finally:
            self._tags[tag][context].pop()

    def inject(self, function):
        annotations = function.__annotations__
        args, va, kw, defaults = inspect.getargspec(function)
        defaults = dict(zip(reversed(args), reversed(defaults)))
        calls = []
        for arg in args:
            if arg in annotations:
                requirement = annotations[arg]
                calls.append(self[requirement])
            else:
                calls.append([defaults[arg]])
        for call in itertools.product(*calls):
            function(*call)

    def __getitem__(self, requirement):
        context = self.context()
        if requirement in self._tags:
            if context in self._tags[requirement]:
                if self._tags[requirement][context]:
                    yield self._tags[requirement][context][-1]
                    return
            if None in self._tags[requirement]:
                if self._tags[requirement][None]:
                    yield self._tags[requirement][None][-1]
                    return
        for identity in reversed(self._stacked):
            if identity.context is not None != self.context():
                continue
            object = self._stacked[identity]
            if isinstance(object, requirement):
                yield object
                break
        else:
            for object in self._objects.itervalues():
                if isinstance(object, requirement):
                    yield object
