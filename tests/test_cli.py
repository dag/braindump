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


def test_application():

    calls = []

    class FirstPlugin(cli.Plugin):

        def create_argparser(self, parser):
            parser.add_argument('--first')

        def build_config(self, builder, args, environ):
            builder.set(first=args.first)

        def run(self, state):
            calls.append(('first', state))

    class SecondPlugin(cli.Plugin):

        def create_argparser(self, parser):
            parser.add_argument('--second')

        def build_config(self, builder, args, environ):
            builder.set(second=args.second)

        def run(self, state):
            calls.append(('second', state))

    class Application(cli.Application):

        argparser = {
            'prog': 'testapp',
        }

        plugins = [
            FirstPlugin(),
            SecondPlugin(),
        ]

    assert not calls

    app = Application()
    env = cli.Environment(arguments=['--first', '1st', '--second', '2nd'])

    # FIXME probably unreliable test
    usage = 'usage: testapp [-h] [--first FIRST] [--second SECOND]\n'
    assert app.argparser.format_usage() == usage

    app(env)

    assert [x[0] for x in calls] == ['first', 'second']
    assert calls[0][1] is calls[1][1]

    state = calls[0][1]
    assert state.app is app and state.environ is env
    assert vars(state.args) == dict(first='1st', second='2nd')
    assert state.config.first == '1st'
    assert state.config.second == '2nd'
