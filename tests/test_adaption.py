import collections
import numbers
import pytest

from braindump import adaption


def test_registry():
    adapt = adaption.Registry()

    adapt.add(format, numbers.Number, basestring)
    assert adapt(3, basestring) == '3'
    assert adapt('hello', basestring) == 'hello'

    with pytest.raises(TypeError):
        adapt(3, unicode)

    with pytest.raises(TypeError):
        adapt(3, collections.Mapping)

    adapt.add(unicode, basestring)
    adapted = adapt('hello', unicode)
    assert adapted == u'hello' and type(adapted) is unicode

    adapted = adapt(3, unicode)
    assert adapted == u'3' and type(adapted) is unicode

    adapt.add(list, tuple)
    adapt.add(set, list)
    adapt.add(dict, set)
    adapted = adapt((('a', 1), ('b', 2)), dict)
    assert adapted == dict(a=1, b=2) and type(adapted) is dict
