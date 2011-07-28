import copy
import pytest

from braindump import cli


def test_config_node():
    node = cli.ConfigNode(one=1, two=2)

    assert repr(node) == 'ConfigNode(one=1, two=2)'

    # fields are attributes
    assert node.one == 1 and node.two == 2
    assert set(dir(node)) == set(['one', 'two'])
    assert set(node) == set(['one', 'two'])

    # nodes are immutable
    with pytest.raises(AttributeError):
        node.two = 'two'
    with pytest.raises(AttributeError):
        node.three = 3


def test_dict_merging(merging):
    # copy the mappings so we can check that they weren't modified
    mappings = copy.deepcopy(merging['mappings'])

    merged = cli.merge(merging['mappings'])
    assert merged == merging['merged']
    assert merging['mappings'] == mappings

    # merge into a new dict rather than in-place of any of the passed ones
    assert not any(merged is mapping for mapping in merging['mappings'])
