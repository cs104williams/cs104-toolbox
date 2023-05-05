import sys
from setuptools import setup

if sys.version_info < (3, 0):
    raise ValueError('This package requires python >= 3.0')

with open('requirements.txt') as fid:
    install_requires = [l.strip() for l in fid.readlines() if l]

with open('cs104/version.py') as fid:
    for line in fid:
        if line.startswith('__version__'):
            version = line.strip().split()[-1][1:-1]
            break

setup(
    name = 'cs104lib',
    packages = ['cs104'],
    package_dir = { 'cs104': 'cs104' },
    version = version,
    install_requires = install_requires,
    description = 'Various tools for CS104',
    long_description = 'Various tools for CS104',
    author = 'Stephen Freund and Katie Keith',
    package_data={"cs104": ["data/*.json"]}
)
