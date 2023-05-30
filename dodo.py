import doit
from doit.action import CmdAction
import os

DOIT_CONFIG = {'default_tasks': ['eng', 'docs']}


def task_gitclean():
    """Clean all generated files from .gitignore rules."""
    return {
            'actions': ['git clean -xdf'],
           }


def task_docs():
    """Create HTML documentation in /build_doc."""
    return {
        'actions': ['sphinx-build -M html doc build_doc'],
    }


def task_tests():
    """Input data testing"""
    return {
        'actions': ['python3 test.py -v']
    }


def task_flake():
    """Check files style according to flake8"""
    return {
        'actions': ['flake8 QuizerBot']
    }


def task_docstyle():
    """Check docstrings against pydocstyle."""
    return {
            'actions': ['pydocstyle QuizerBot']
           }


def task_eng():
    """Translate into Englist."""
    babel_cfg = 'QuizerBot/l10n/eng/LC_MESSAGES/newbot.mo'

    return {
        'actions': ['pybabel compile -D newbot -d QuizerBot/l10n -l eng'],
        'targets': [babel_cfg]
    }


def task_rus():
    """Translate into Russian."""

    def create_cmd_string(x):
        return "echo Succesfully russified!" if x else "echo It has already russified, nothing to do."

    if x := os.path.exists('QuizerBot/l10n/eng/LC_MESSAGES/newbot.mo'):
        os.remove('QuizerBot/l10n/eng/LC_MESSAGES/newbot.mo')
    return {
        'actions': [CmdAction(create_cmd_string(x))],
        'verbosity': 2,
        }


def task_wheel():
    """Create a wheel"""
    return {
        'actions': ['python3 -m build -w -n']
    }
