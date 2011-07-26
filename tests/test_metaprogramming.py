import contextlib
import pkg_resources
import pytest
import yaml

import metaprogramming


with contextlib.closing(
    pkg_resources.resource_stream(__name__, 'identifiers.yml')
) as stream:

    identifier_fixtures = yaml.load(stream)


def test_encoding_identifiers():
    for input, result in identifier_fixtures['encode'].iteritems():
        assert metaprogramming.to_identifier(unicode(input)) == result
