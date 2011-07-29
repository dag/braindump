import abc
import ConfigParser as configparser
import contextlib
import copy
import json
import os
import pkg_resources
import yaml

from . import meta


class Node(object):

    __slots__ = ('__children',)

    def __init__(self, **children):
        self.__children = {}
        for key, value in children.iteritems():
            if isinstance(value, dict):
                self.__children[key] = type(self)(**value)
            else:
                self.__children[key] = value

    def __getattr__(self, name):
        try:
            return self.__children[name]
        except KeyError:
            raise AttributeError(name)

    def __contains__(self, path):
        try:
            self[path]
        except KeyError:
            return False
        return True

    def __getitem__(self, path):
        names = map(meta.string_to_identifier, path.split(u'.'))
        try:
            return reduce(getattr, [self] + names)
        except AttributeError:
            raise KeyError(path)

    def __dir__(self):
        return self.__children.keys()

    def __iter__(self):
        return iter(self.__children)

    def __eq__(self, other):
        return (isinstance(other, type(self)) and
                self.__children == other._Node__children)

    def __repr__(self):
        children = ', '.join('{0}={1!r}'.format(*item)
                             for item in sorted(self.__children.iteritems()))
        return '{0}({1})'.format(type(self).__name__, children)


def convert_keys(mapping, converter=meta.string_to_identifier):
    if not isinstance(mapping, dict):
        return mapping
    new = {}
    for key, value in mapping.iteritems():
        new[converter(key)] = convert_keys(value, converter)
    return new


def merge(mappings):
    merged = {}
    for mapping in mappings:
        stack = [(merged, mapping)]
        while stack:
            destination, source = stack.pop()
            for key in source:
                value = copy.copy(source[key])
                if key not in destination:
                    destination[key] = value
                    continue
                if all(isinstance(x, dict)
                       for x in [value, destination[key]]):
                    stack.append((destination[key], value))
                    continue
                destination[key] = value
    return merged


class AbstractLoader(object):

    __metaclass__ = abc.ABCMeta

    def get_location(self, spec):
        if u':' not in spec:
            return None, spec
        return spec.split(u':', 1)

    def get_stream(self, spec):
        package, name = self.get_location(spec)
        if package:
            stream = pkg_resources.resource_stream(package, name)
            return contextlib.closing(stream)
        return open(name)

    def get_filename(self, spec):
        package, name = self.get_location(spec)
        if package:
            return pkg_resources.resource_filename(package, name)
        return name

    def get_string(self, spec):
        package, name = self.get_location(spec)
        if package:
            return pkg_resources.resource_string(package, name)
        with open(name) as stream:
            return stream.read()

    @abc.abstractmethod
    def __call__(self, spec):
        pass


class AbstractStreamLoader(AbstractLoader):

    @abc.abstractproperty
    def function(self):
        pass

    def __call__(self, spec):
        with self.get_stream(spec) as stream:
            return self.function.__func__(stream)


class YAMLLoader(AbstractStreamLoader):

    function = yaml.load


class JSONLoader(AbstractStreamLoader):

    function = json.load


class INILoader(AbstractLoader):

    def __call__(self, spec):
        parser = configparser.RawConfigParser()
        with self.get_stream(spec) as stream:
            parser.readfp(stream, spec)
        mapping = {}
        for section in parser.sections():
            mapping[section] = {}
            for option, value in parser.items(section):
                try:
                    value = parser.getint(section, option)
                except ValueError:
                    try:
                        value = parser.getfloat(section, option)
                    except ValueError:
                        try:
                            value = parser.getboolean(section, option)
                        except ValueError:
                            pass
                mapping[section][option] = value
        return mapping


class Builder(object):

    def __init__(self):
        self._settings = []
        self._loaders = {}

    def add_loader(self, ext, loader):
        assert ext not in self._loaders
        self._loaders[ext] = loader

    def set(self, **settings):
        self._settings.append(settings)

    def load(self, source):
        if isinstance(source, basestring):
            root, ext = os.path.splitext(source)
            loader = self._loaders[ext]
            self.set(**loader(source))
        else:
            self.set(**source)

    def build(self):
        safe = map(convert_keys, self._settings)
        merged = merge(safe)
        config = Node(**merged)
        return config
