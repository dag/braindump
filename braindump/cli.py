import os
import subprocess
import sys


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
