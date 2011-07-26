import keyword
import re


def to_identifier(string):
    ident = re.sub(r'[^a-zA-Z0-9]+', '_', string)
    ident = ident.strip('_')
    if ident[0].isdigit():
        ident = '_' + ident
    if keyword.iskeyword(ident):
        ident += '_'
    return ident
