import collections
import numbers
import pytest

from braindump import adaption


def test_registry():
    adapt = adaption.Registry()

    adapt[numbers.Number:basestring] = format
    assert adapt(3, basestring) == '3'
    assert adapt('hello', basestring) == 'hello'

    with pytest.raises(TypeError):
        adapt(3, unicode)

    with pytest.raises(TypeError):
        adapt(3, collections.Mapping)

    adapt[basestring:unicode] = unicode
    adapted = adapt('hello', unicode)
    assert adapted == u'hello' and type(adapted) is unicode

    adapted = adapt(3, unicode)
    assert adapted == u'3' and type(adapted) is unicode

    adapt[tuple:list] = list
    adapt[list:set] = set
    adapt[set:dict] = dict
    adapted = adapt((('a', 1), ('b', 2)), dict)
    assert adapted == dict(a=1, b=2) and type(adapted) is dict


def test_registry_type_factories():
    adapt = adaption.Registry()

    assert adapt[str] is str

    adapt[str] = unicode
    assert adapt[str] is unicode

    adapt[str] = int
    assert adapt[str] is int

    del adapt[str]
    assert adapt[str] is str
