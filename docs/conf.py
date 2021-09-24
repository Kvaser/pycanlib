# -*- coding: utf-8 -*-
# pylint: skip-file
"""Configuration for Sphinx."""

from __future__ import unicode_literals

import os

import sphinx_rtd_theme

with open("../canlib/__about__.py") as fp:
    exec(fp.read())

try:
    with open("../canlib/__version__.py") as fp:
        exec(fp.read())
except IOError:
    __version__ = __dummy_version__

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.extlinks',
    'sphinx.ext.ifconfig',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
]
if os.getenv('SPELLCHECK'):
    extensions += 'sphinxcontrib.spelling'
    spelling_show_suggestions = True
    spelling_lang = 'en_US'


source_suffix = '.rst'
master_doc = 'index'
project = __title__
year = __year__
author = '{a} <{e}>'.format(a=__author__, e=__email__)
copyright = __copyright__
version = release = __version__

default_role = 'py:obj'

# RTD packages pygment styles inside its theme.css and cannot be overridden:
# https://github.com/snide/sphinx_rtd_theme/blob/master/sass/theme.sass#L45
# pygments_style = 'trac'  # 'igor'  # 'trac'
# templates_path = ['.']

html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

html_last_updated_fmt = '%a, %d %b %Y'
html_split_index = False
html_sidebars = {
    '**': ['searchbox.html', 'globaltoc.html', 'sourcelink.html'],
}
# html_short_title = '%s-%s' % (project, version)

# Get Windows line endings in Relnotes for Finn in nightly build
text_newlines = 'native'

napoleon_use_ivar = True
napoleon_use_rtype = False
napoleon_use_param = False
# napoleon_google_docstring = False
# https://michaelgoerz.net/notes/extending-sphinx-napoleon-docstring-sections.html
# https://samnicholls.net/2016/06/15/how-to-sphinx-readthedocs/
