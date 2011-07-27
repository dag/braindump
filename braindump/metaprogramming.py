import keyword
import re


def string_to_identifier(string):
    ident = re.sub(r'[^a-zA-Z0-9]+', '_', string)
    ident = ident.strip('_')
    if ident[0].isdigit():
        ident = '_' + ident
    if keyword.iskeyword(ident):
        ident += '_'
    return ident


def identifier_to_string(identifier):
    string = re.sub(r'([A-Z][^A-Z_])', r'_\1', identifier)
    string = string.strip('_')
    string = re.sub(r'_+', '-', string)
    string = string.lower()
    return unicode(string)
