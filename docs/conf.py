# -*- coding: utf-8 -*-
# pylint: skip-file
"""Configuration for Sphinx."""

from __future__ import unicode_literals

import datetime
import os
import sys
from importlib.metadata import metadata, version
from pathlib import Path

import sphinx_rtd_theme

# autodoc imports `canlib`, which loads the native CANlib libraries. Default to
# the mock path so docs build without the SDK present (see dllLoader.load_dll).
os.environ.setdefault("READTHEDOCS", "True")

# Make the project root importable so the relnotes generator can be called below.
_ROOT = next(p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").exists())
sys.path.insert(0, str(_ROOT))

_meta = metadata("canlib")
__title__ = _meta.get("Name", "canlib")
# pyproject `authors` emits a combined "Name <email>" Author-email field.
_author_email = _meta.get("Author-email", "Kvaser AB <support@kvaser.com>")
_name, _, _addr = _author_email.partition("<")
__author__ = _name.strip() or "Kvaser AB"
__email__ = _addr.rstrip(">").strip() or "support@kvaser.com"
__version__ = version("canlib")

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

# Files included via `.. include::` or used only as build input, not standalone
# documents — keep Sphinx from parsing them and emitting toctree warnings.
exclude_patterns = ['_readme_intro.rst']

project = __title__
year = datetime.date.today().year
author = '{a} <{e}>'.format(a=__author__, e=__email__)
copyright = '{y} {a}'.format(y=year, a=__author__)
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


def setup(app):
    """Generate the release notes before the build so they are never stale.

    Inhouse (the release-notes template is present), regenerate ``Relnotes.rst``
    at the project root from the template, using the git-tag version. In the
    public repo the template and ``scripts/`` are not shipped, so the committed
    ``Relnotes.rst`` is used as-is. Either way it is copied into this ``docs/``
    directory so the ``Relnotes`` toctree entry resolves.
    """
    import shutil

    docs_dir = Path(__file__).resolve().parent
    root_relnotes = _ROOT / "Relnotes.rst"
    template = _ROOT / "releasenotes_template.rst"

    def _relnotes(app, config):
        if template.exists():
            from scripts.pybuild.generate_relnotes import generate

            generate()
        if root_relnotes.exists():
            shutil.copyfile(root_relnotes, docs_dir / "Relnotes.rst")

    app.connect("config-inited", _relnotes)
# napoleon_google_docstring = False
# https://michaelgoerz.net/notes/extending-sphinx-napoleon-docstring-sections.html
# https://samnicholls.net/2016/06/15/how-to-sphinx-readthedocs/
