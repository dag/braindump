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


def test_registry_tagging():
    registry = component.Registry()
    tagged = list(registry['registry'])
    assert tagged == [registry] and tagged[0] is registry
    registry.tag('foo', 'bar')
    assert list(registry['foo']) == ['bar']


def test_isinstance_predicate():
    Percentage = component.predicate(lambda x: 0 <= x <= 100)
    assert isinstance(50, Percentage)
    assert not isinstance(150, Percentage)


def test_require():
    @component.require(c=3, e=5)
    @component.require(1, 2)
    @component.require(d=4)
    def annotated(a, b, c, d, e, f): pass
    assert annotated.__annotations__ == dict(a=1, b=2, c=3, d=4, e=5)


def test_dependency_injection():
    calls = []
    @component.require(num=int, nums=tuple)
    def dependable(num, nums, x=42, *args, **kwargs):
        assert x == 42 and args == () and kwargs == {}
        calls.append((num, nums))

    registry = component.Registry()
    registry.add(2)
    registry.add(5)
    registry.add((10, 20, 30))
    registry.add((3, 6, 9))
    registry.inject(dependable)

    assert len(calls) == 4
    assert set(calls) == set([
        (2, (10, 20, 30)),
        (2, (3, 6, 9)),
        (5, (10, 20, 30)),
        (5, (3, 6, 9)),
    ])
