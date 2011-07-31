import io
import os
import sys

from braindump import cli


def test_environment_defaults():
    env = cli.Environment()
    assert env.arguments == sys.argv and env.arguments is not sys.argv
    assert env.variables == os.environ and env.variables is not os.environ
    assert env.streams == dict(input=sys.stdin, output=sys.stdout, error=sys.stderr)


def test_environment_overrides():
    env = cli.Environment(arguments=['one', 'two'])
    assert env.arguments == ['one', 'two']

    env = cli.Environment(variables={'one': '1', 'two': '2'})
    assert env.variables == {'one': '1', 'two': '2'}

    stdin, stdout, stderr = io.BytesIO(), io.BytesIO(), io.BytesIO()

    env = cli.Environment(streams=dict(input=stdin))
    assert env.streams == dict(input=stdin, output=sys.stdout, error=sys.stderr)

    env = cli.Environment(streams=dict(output=stdout))
    assert env.streams == dict(input=sys.stdin, output=stdout, error=sys.stderr)

    env = cli.Environment(streams=dict(error=stderr))
    assert env.streams == dict(input=sys.stdin, output=sys.stdout, error=stderr)
