import collections
import numbers

from braindump import component


def test_registry():
    registry = component.Registry()
    registry.add(2)
    registry.add(5)
    registry.add('bytes')
    registry.add(u'unicode')
    registry.add(dict(key='value'))

    assert set(registry[numbers.Number]) == set([2, 5])
    assert set(registry[basestring]) == set(['bytes', u'unicode'])
    assert set(registry[unicode]) == set([u'unicode'])
    assert next(registry[collections.Mapping]) == dict(key='value')


def test_registry_hashable():
    registry = component.Registry()
    registry.add('hashable')
    registry.add('hashable')
    assert list(registry[str]) == ['hashable']


def test_registry_unhashable():
    registry = component.Registry()
    registry.add(dict(key='value'))
    registry.add(dict(key='value'))
    assert list(registry[dict]) == [dict(key='value'), dict(key='value')]


def test_registry_object_id():
    registry = component.Registry()
    mapping = dict(key='value')
    registry.add(mapping)
    registry.add(mapping)
    dicts = list(registry[dict])
    assert dicts == [mapping] and dicts[0] is mapping


def test_registry_stacks():
    registry = component.Registry()
    registry.add(0)
    registry.add(1)
    assert set(registry[int]) == set([0, 1])
    with registry.stack(2):
        assert list(registry[int]) == [2]
        with registry.stack(3):
            assert list(registry[int]) == [3]
        assert list(registry[int]) == [2]
    assert set(registry[int]) == set([0, 1])
