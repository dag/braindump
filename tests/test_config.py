import copy
import pytest

from braindump import config


def test_node():
    node = config.Node(one=1, two=2)

    assert repr(node) == 'Node(one=1, two=2)'

    # children are attributes
    assert node.one == 1 and node.two == 2
    assert set(dir(node)) == set(['one', 'two'])
    assert set(node) == set(['one', 'two'])
    assert hasattr(node, 'one') and hasattr(node, 'two')
    assert not hasattr(node, 'three')

    # nodes are immutable
    with pytest.raises(AttributeError):
        node.two = 'two'
    with pytest.raises(AttributeError):
        node.three = 3


def test_node_traversal():
    node = config.Node(greetings=dict(english='Hello', swedish='Hej'))

    assert 'greetings' in node
    assert 'greetings.english' in node
    assert 'greetings.swedish' in node
    assert 'missing' not in node

    assert node['greetings'] is node.greetings
    assert node['greetings.english'] is node.greetings.english
    assert node['greetings.swedish'] is node.greetings.swedish

    with pytest.raises(KeyError):
        node['missing']

    node = config.Node(class_=dict(is_='a keyword'))
    assert 'class.is' in node
    assert node['class.is'] is node.class_.is_


def test_key_conversion():
    mapping = config.convert_keys({
        'class': 'keyword',
        '5': 'number',
        ' arbitrarily-complex %KEY!!': 'encoded',
        'nested': {'import': 'also keyword'},
    })

    assert mapping == dict(
        class_='keyword',
        _5='number',
        arbitrarily_complex_key='encoded',
        nested=dict(import_='also keyword'),
    )


def test_dict_merging(merging):
    # copy the mappings so we can check that they weren't modified
    mappings = copy.deepcopy(merging['mappings'])

    merged = config.merge(merging['mappings'])
    assert merged == merging['merged']
    assert merging['mappings'] == mappings

    # merge into a new dict rather than in-place of any of the passed ones
    assert not any(merged is mapping for mapping in merging['mappings'])


def test_builder():
    builder = config.Builder()

    builder.add({
        'numbers': dict(one=1, two=2, three=4),
        'greetings': dict(english='Hello', swedish='Hej'),
    })

    builder.add({
        'numbers': dict(two=2, three=3, four=4),
        'greetings': dict(lojban='coi'),
    })

    builder.add({
        'class': 'keyword',
        '5': 'number',
        ' arbitrarily-complex %KEY!!': 'encoded',
    })

    builder.add({'merge-by-converted-key': dict(one=1, two=2)})
    builder.add({'merge_by_converted_key': dict(three=3, four=4)})

    conf = builder.build()
    assert conf == config.Node(
        numbers=config.Node(one=1, two=2, three=3, four=4),
        greetings=config.Node(english='Hello', swedish='Hej', lojban='coi'),
        class_='keyword', _5='number', arbitrarily_complex_key='encoded',
        merge_by_converted_key=config.Node(one=1, two=2, three=3, four=4),
    )
