import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand


if sys.version_info < (3, 0):
    raise ValueError('This package requires python >= 3.0')

with open('requirements.txt') as fid:
    install_requires = [l.strip() for l in fid.readlines() if l]

tests_requires = [

]


with open('cs104/version.py') as fid:
    for line in fid:
        if line.startswith('__version__'):
            version = line.strip().split()[-1][1:-1]
            break

class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ['--nbval-lax', '--cov=datascience', 'tests']

    def finalize_options(self):
        TestCommand.finalize_options(self)

    def pytest_collectstart(collector):
        collector.skip_compare += 'text/html'

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name = 'cs104-toolbox',
    packages = ['cs104'],
    package_dir = { 'cs104': 'cs104' },
    version = version,
    install_requires = install_requires,
    tests_require = tests_requires,
    cmdclass = {'test': PyTest},
    description = 'Various tools for CS104',
    long_description = 'Various tools for CS104',
    author = 'Stephen Freund and Katie Keith',
    package_data={"cs104": ["data/*.json"]}
)
