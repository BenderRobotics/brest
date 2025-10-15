# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

import os
import sys
sys.path.insert(0, os.path.abspath('..'))


# -- Project information -----------------------------------------------------
# Variable "version" is automatically used as version identifier. (#PY-001)
from brest import __version__ as version


project = 'Brest'
copyright = '2024, Bender Robotics'
author = 'Bender Robotics'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
master_doc = 'index'
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "m2r2"
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'pyserial': ('https://pyserial.readthedocs.io/en/latest/', None),
}

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', 'README.md']

# Autodoc default options
autodoc_default_options = {
    'member-order': 'bysource',
}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# Using a external theme.
import sphinx_rtd_theme

extensions.append("sphinx_rtd_theme")

html_theme = "sphinx_rtd_theme"

# Template configuration (#PY-004)
html_theme_options = {
    'style_nav_header_background': '#d01242',
    'prev_next_buttons_location': None,
    # TOC
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'display_version': True,
    'titles_only': False
}

# Path to logo picture to be used #PY-005
# html_logo = r'.\_static\logo.png'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
html_css_files = [
    'brest.css'
]

# Configuration for sphinx-versions
# https://sphinx-versions.readthedocs.io/en/latest/settings.html
import re

branch = 'none'
is_ci = os.getenv('GITLAB_CI', False)

if not is_ci:
    def get_active_branch_name():
        head_dir = os.path.join(os.path.dirname(__file__), '..', '.git', 'HEAD')
        if not os.path.exists(head_dir):
            return 'none'   # when run as older version, it is offline too, and should not look for HEAD
        with open(head_dir, mode='r') as f:
            content = f.read().splitlines()

        for line in content:
            if line[0:4] == "ref:":
                return line.partition("refs/heads/")[2]

    branch = get_active_branch_name()

is_tag = os.getenv('CI_COMMIT_TAG', '')
branch = os.getenv('CI_COMMIT_BRANCH', branch)
include_branch = os.getenv('INCLUDE_CURRENT_BRANCH', '1')

if not is_tag and include_branch != '0':
    current_branch = branch
else:
    current_branch = 'none'

# current_branch = 'none'             # By default and upon tagging there should always be 'none'
                                    # For doc update testing, enter name of the branch
                                    # (e.g. r'feature/3465-doc-design-and-version')
                                    #   - for viewing switch doc version to the branch once it is generated

scv_root_ref = 'devel'              # Make devel the root reference
scv_greatest_tag = True             # The greatest tag is the landing page
scv_show_banner = True              # Show warning banner when viewing older docs version
scv_banner_greatest_tag = True      # Make the greatest tag the "up-to-date" version
scv_sort = ('semver',)              # Sort version by semantic versioning
scv_whitelist_branches = (current_branch, )
scv_whitelist_tags = (              # Tag filtering:
    # Main releases are enabled
    re.compile(r'^[0-9]+\.[0-9]+\.[0-9]+$'),
    # Tags for doc update are enabled
    re.compile(r'^([0-9]+\.[0-9]+\.[0-9]+)\.doc$'),
)
scv_blacklist_tags = (
    # Releases 0.0.2-0.0.12 are disabled (old versions of docs replace by *.doc releases)
    # Releases older than 0.0.10 are disabled altogether (not relevant anymore)
    re.compile(r'^0\.0\.[0-9](\.doc)?$'),
    re.compile(r'^0\.0\.1[0-2]$'),
    re.compile(r'^0\.0\.14$'),
)
scv_delete_static = True            # Delete `_static`, `.doctree` from each version (except root)
