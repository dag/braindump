import argparse
import os
import subprocess
import sys

from . import config


def less(iterable):  # pragma: no cover (not quite sure how to test)
    proc = subprocess.Popen(['less', '-FRX'], stdin=subprocess.PIPE)
    with proc.stdin:
        for chunk in iterable:
            proc.stdin.write(chunk)
    proc.wait()


class Environment(object):

    arguments = None

    variables = None

    streams = None

    def __init__(self, arguments=None, variables=None, streams=None):
        self.arguments = list(sys.argv if arguments is None else arguments)
        self.variables = dict(os.environ if variables is None else variables)
        self.streams = dict(input=sys.stdin, output=sys.stdout, error=sys.stderr)
        if streams is not None:
            self.streams.update(streams)


class State(object):

    def __init__(self, app, config, args, environ):
        self.app = app
        self.config = config
        self.args = args
        self.environ = environ


class Plugin(object):  # pragma: no cover (abstract)

    def create_argparser(self, parser):
        pass

    def build_config(self, builder, args, environ):
        pass

    def run(self, state):
        pass


class Application(object):

    argparser = {}

    plugins = []

    @classmethod
    def main(cls):
        app = cls()
        app()

    def __init__(self):
        self.plugins = list(self.plugins)
        self.create_argparser()

    def create_argparser(self):
        self.argparser = argparse.ArgumentParser(**self.argparser)
        for plugin in self.plugins:
            plugin.create_argparser(self.argparser)

    def build_config(self, args, environ):
        builder = config.Builder()
        builder.add_loader('.yml', config.YAMLLoader())
        for plugin in self.plugins:
            plugin.build_config(builder, args, environ)
        return builder.build()

    def __call__(self, environ=None):
        if environ is None:
            environ = Environment()
        args = self.argparser.parse_args(environ.arguments)
        config = self.build_config(args, environ)
        state = State(self, config, args, environ)
        for plugin in self.plugins:
            plugin.run(state)
