from setuptools import Command, find_packages, setup

pytest = "pytest >=3.3.0"
pytest_cov = "pytest-cov >=2.5.1"
pandas = "pandas >=1.2.3"
sphinx = "sphinx >=1.6.5"
sphinx_rtd_theme = "sphinx_rtd_theme >=0.2.4"


extras_require = {
    "dev": [pytest, pytest_cov, sphinx, sphinx_rtd_theme],
    "test": [pytest, pandas],
}

setup_require = [
    sphinx,
    sphinx_rtd_theme,
]


def readme():
    with open('README.rst') as f:
        return f.read()


with open("canlib/__about__.py") as fp:
    exec(fp.read())

try:
    with open("canlib/__version__.py") as fp:
        exec(fp.read())
# IOError is an alias for OSError in python 3, while FileNotFoundError
# does not exist in python 2
except IOError:
    __version__ = __dummy_version__


class PurgePycCmd(Command):
    description = "Recurse through all subdirectories and remove all .pyc files"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import glob
        import os

        for filename in glob.glob("./**/*.pyc", recursive=True):
            print("Deleting:", filename)
            os.remove(filename)


setup(
    name=__title__,
    version=__version__,
    description=__summary__,
    long_description=readme(),
    url=__uri__,
    author=__author__,
    author_email=__email__,
    license=__license__,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    keywords='development',
    packages=find_packages(exclude=['tests']),
    test_suite='nose.collector',
    extras_require=extras_require,
    tests_require=['nose'],  # pytest>=3.0 for approx, tox >=2.9.1
    setup_requires=setup_require,
    # entry_points={
    #     "distutils.commands": [
    #         "purge_pyc = PurgePycCmd()"]
    # },
    install_requires=[
        "pydantic >=1.8.1",
    ],
    cmdclass={
        'purge_pyc': PurgePycCmd,
    },
)
