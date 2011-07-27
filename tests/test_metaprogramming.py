from braindump import metaprogramming


def test_string_to_identifier(string_to_identifier):
    for string, identifier in string_to_identifier.iteritems():
        result = metaprogramming.string_to_identifier(unicode(string))
        assert result == identifier


def test_identifier_to_string(identifier_to_string):
    for identifier, string in identifier_to_string.iteritems():
        result = metaprogramming.identifier_to_string(identifier)
        assert result == unicode(string)
