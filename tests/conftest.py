import glob
import os
import yaml


HERE = os.path.dirname(__file__)


def pytest_generate_tests(metafunc):
    for filename in glob.iglob(os.path.join(HERE, 'fixtures', '*.yml')):
        name, ext = os.path.splitext(os.path.basename(filename))
        if name in metafunc.funcargnames:
            with open(filename) as stream:
                for doc in yaml.load_all(stream):
                    metafunc.addcall(funcargs={name: doc})
