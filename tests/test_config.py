import copy
import os
import pytest

from braindump import config


def _relative(*path):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), *path))


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


def test_abstract_loader():
    class FakeLoader(config.AbstractLoader):
        __call__ = None
    loader = FakeLoader()

    package, name = loader.get_location('tests.fixtures:configs/one.yml')
    assert package == 'tests.fixtures' and name == 'configs/one.yml'

    package, name = loader.get_location('configs/one.yml')
    assert not package and name == 'configs/one.yml'

    package, name = loader.get_location(':configs/with:colon.yml')
    assert not package and name == 'configs/with:colon.yml'

    with loader.get_stream('tests.fixtures:configs/one.yml') as stream:
        streamed = stream.read()
    string = loader.get_string('tests.fixtures:configs/one.yml')
    assert streamed == string == 'numbers:\n  one: 1\n'

    with loader.get_stream(_relative('fixtures/configs/one.yml')) as stream:
        streamed = stream.read()
    string = loader.get_string(_relative('fixtures/configs/one.yml'))
    assert streamed == string == 'numbers:\n  one: 1\n'

    filename = loader.get_filename('tests.fixtures:configs/one.yml')
    assert filename == _relative('fixtures/configs/one.yml')

    filename = loader.get_filename(_relative('fixtures/configs/one.yml'))
    assert filename == _relative('fixtures/configs/one.yml')


def test_yaml_loader():
    loader = config.YAMLLoader()

    one = loader(_relative('fixtures/configs/one.yml'))
    assert one == dict(numbers=dict(one=1))

    two = loader('tests.fixtures:configs/two.yml')
    assert two == dict(numbers=dict(two=2))


def test_json_loader():
    loader = config.JSONLoader()

    one = loader(_relative('fixtures/configs/one.json'))
    assert one == dict(numbers=dict(one=1))

    two = loader('tests.fixtures:configs/two.json')
    assert two == dict(numbers=dict(two=2))


def test_ini_loader():
    loader = config.INILoader()
    mapping = dict(types=dict(int=1, float=3.14, boolean=True, string='also'))

    assert loader(_relative('fixtures/configs/one.ini')) == mapping
    assert loader('tests.fixtures:configs/one.ini') == mapping


def test_builder():
    builder = config.Builder()

    builder.set(
        numbers=dict(one=1, two=2, three=4),
        greetings=dict(english='Hello', swedish='Hej'),
    )

    builder.set(
        numbers=dict(two=2, three=3, four=4),
        greetings=dict(lojban='coi'),
    )

    builder.load({
        'class': 'keyword',
        '5': 'number',
        ' arbitrarily-complex %KEY!!': 'encoded',
    })

    builder.load({'merge-by-converted-key': dict(one=1, two=2)})
    builder.load({'merge_by_converted_key': dict(three=3, four=4)})

    conf = builder.build()
    assert conf == config.Node(
        numbers=config.Node(one=1, two=2, three=3, four=4),
        greetings=config.Node(english='Hello', swedish='Hej', lojban='coi'),
        class_='keyword', _5='number', arbitrarily_complex_key='encoded',
        merge_by_converted_key=config.Node(one=1, two=2, three=3, four=4),
    )


def test_builder_add_loader():
    builder = config.Builder()

    builder.add_loader('.json', config.JSONLoader())
    builder.add_loader('.yml', config.YAMLLoader())
    with pytest.raises(AssertionError):
        builder.add_loader('.yml', config.YAMLLoader())

    builder.load('tests.fixtures:configs/one.yml')
    builder.load('tests.fixtures:configs/two.json')
    builder.load(_relative('fixtures/configs/three.yml'))

    conf = builder.build()
    assert conf == config.Node(
        numbers=config.Node(one=1, two=2, three=3),
    )

    builder.reset()
    conf = builder.build()
    assert conf == config.Node()

    # ambiguous spec
    with pytest.raises(AssertionError):
        builder.load('tests.fixtures:configs/one')

    # unambiguous, only three.yml exists
    builder.load('tests.fixtures:configs/three')

    conf = builder.build()
    assert conf == config.Node(numbers=config.Node(three=3))
