from braindump import metaprogramming


def test_encoding_identifiers(string_to_identifier):
    for string, identifier in string_to_identifier.iteritems():
        assert metaprogramming.to_identifier(unicode(string)) == identifier
