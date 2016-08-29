from setuptools import setup

from ia_recent import \
    __title__, __version__, __url__, __author__, __email__, __license__,  __doc__


setup(
    name=__title__,
    version=__version__,
    author=__author__,
    author_email=__email__,
    url=__url__,
    license=__license__,
    description=__doc__.splitlines()[0],
    py_modules=[__title__],
    install_requires=[
        'internetarchive',
        'docopt',
    ],
    entry_points={
        'internetarchive.cli.plugins': [
            __title__ + ' = ' + __title__,
        ],
        'console_scripts': [
            __title__.replace('_', '-') + ' = ' + __title__ + ':main',
        ],
    },
    tests_require=[
        'pytest',
        'pytest-pep8',
    ],
)
