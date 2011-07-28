import collections
import functools
import venusian


class Recorder(object):

    name = None

    @classmethod
    def named(cls, name):
        return type(cls.__name__, (cls,), dict(name=name))

    def __init__(self, decorator):
        functools.update_wrapper(self, decorator)
        self.decorator = decorator
        if self.name is None:
            self.name = decorator.__name__

    def __call__(self, *args, **kwargs):

        def callback(scanner, name, ob):
            scanner.registry.add_record(
                self.name, ob, args, kwargs, scanner.params)

        def attach_callback(target):
            venusian.attach(target, callback, 'braindump.registry')
            return target

        return attach_callback


Record = collections.namedtuple(
    'Record', [
        'object',
        'args',
        'kwargs',
        'params',
    ]
)


class Registry(collections.Mapping):

    def __init__(self):
        self._records = {}

    def __getitem__(self, name):
        return self._records[name]

    def __iter__(self):
        return iter(self._records)

    def __len__(self):
        return len(self._records)

    def add_record(self, name, object, args, kwargs, params):
        if name not in self._records:
            self._records[name] = []
        self._records[name].append(Record(object, args, kwargs, params))

    def scan(self, package, **params):
        scanner = venusian.Scanner(registry=self, params=params)
        scanner.scan(package, categories=('braindump.registry',))
