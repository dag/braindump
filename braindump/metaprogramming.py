import keyword
import re


class Split(object):

    def __init__(self, string):
        self._string = unicode(string)

    @property
    def whitespace(self):
        return self._string.split()

    @property
    def words(self):
        return re.findall(ur'[A-Za-z0-9]+', self._string)

    @property
    def mixed(self):
        return re.findall(ur'.+?(?=[A-Z]|$)', self._string)

    @property
    def camel(self):
        return re.findall(ur'[A-Z][^A-Z]*', self._string)

    @property
    def initials(self):
        return re.findall(ur'[A-Z].*?(?=[A-Z][^A-Z]|$)', self._string)

    @property
    def smart(self):
        pattern = ur"""
            [a-z0-9]+
          | [A-Z] [a-z0-9]+
          | [A-Z0-9]+? (?= [A-Z] [a-z0-9] )
          | [A-Z0-9]+
        """
        return re.findall(pattern, self._string, re.X)


class Casing(object):

    def __init__(self, words):
        self._words = map(unicode, words)

    def __repr__(self):
        return u'Casing({0!r})'.format(self._words)

    @property
    def upper(self):
        return u'_'.join(self._words).upper()

    @property
    def lower(self):
        return u'_'.join(self._words).lower()

    @property
    def mixed(self):
        camel = self.camel
        return camel[0].lower() + camel[1:]

    @property
    def camel(self):
        return u''.join(map(unicode.capitalize, self._words))

    @property
    def acronymic(self):
        return u''.join(word[0].upper() + word[1:] for word in self._words)

    @property
    def ident(self):
        ident = Casing(Split(u','.join(self._words)).words).lower
        if ident[0].isdigit():
            return u'_' + ident
        if keyword.iskeyword(ident):
            return ident + u'_'
        return ident

    @property
    def slug(self):
        return self.lower.replace(u'_', u'-')


def string_to_identifier(string):
    return Casing(Split(string).words).ident


def identifier_to_string(identifier):
    return Casing(Split(identifier).smart).slug
