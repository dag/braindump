import collections
import sys

from braindump import venus


@venus.Recorder
def configure(*args, **kwargs):
    pass


@venus.Recorder.named('named_recorder')
def hook():
    pass


@configure(1, 2, 3, four=4)
def configurable():
    pass


@hook()
def hooked():
    pass


def test_registry():
    registry = venus.Registry()
    assert isinstance(registry, collections.Mapping)

    registry.scan(sys.modules[__name__], five=5)

    # keys correspond to recorder names
    assert set(registry) == set(['configure', 'named_recorder'])

    # values are mutable sequences
    assert all(isinstance(value, collections.MutableSequence)
               for value in registry.itervalues())

    for collection in registry.itervalues():
        for record in collection:

            # records are tuple-like
            assert isinstance(record, collections.Sequence)

            # records are quadruples
            assert len(record) == 4

            # records are namedtuple-like
            assert record.object is record[0]
            assert record.args is record[1]
            assert record.kwargs is record[2]
            assert record.params is record[3]

    def is_first_configurable(record):
        try:
            assert record.object is configurable
            assert record.args == (1, 2, 3)
            assert record.kwargs == dict(four=4)
            assert record.params == dict(five=5)
        except AssertionError:
            return False
        return True

    # the configuration for the 'configurable' function was recorded
    assert any(map(is_first_configurable, registry['configure']))

    def is_first_hooked(record):
        try:
            assert record.object is hooked
            assert record.args == ()
            assert record.kwargs == {}
            assert record.params == dict(five=5)
        except AssertionError:
            return False
        return True

    # the hooking of the 'hooked' function was recorded
    assert any(map(is_first_hooked, registry['named_recorder']))
