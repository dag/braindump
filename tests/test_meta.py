from braindump import meta


def test_string_to_identifier(string_to_identifier):
    for string, identifier in string_to_identifier.iteritems():
        result = meta.string_to_identifier(unicode(string))
        assert result == identifier


def test_identifier_to_string(identifier_to_string):
    for identifier, string in identifier_to_string.iteritems():
        result = meta.identifier_to_string(identifier)
        assert result == unicode(string)


def test_splitting(splits):
    for string, variants in splits.iteritems():
        splitter = meta.Split(string)
        for variant, value in variants.iteritems():
            split = getattr(splitter, variant)
            assert split == value
            for word in split:
                assert type(word) is unicode


def test_casing(casings):
    casing = meta.Casing(casings['words'])
    if 'repr' in casings:
        assert repr(casing) == casings['repr']
    for case, value in casings['cases'].iteritems():
        cased = getattr(casing, case)
        assert cased == value and type(cased) is unicode
