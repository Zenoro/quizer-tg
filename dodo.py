import doit
from doit.action import CmdAction
import os


def task_gitclean():
    """Clean all generated files from .gitignore rules."""
    return {
            'actions': ['git clean -xdf'],
           }


def task_generate_docs():
    """Create HTML documentation in /build."""
    return {
        'actions': ['sphinx-build -M html doc build'],
    }


def task_eng():
    """Translate into Englist."""
    locales_dir = 'newbot.pot'
    babel_cfg = 'l10n/eng/LC_MESSAGES/newbot.mo'

    return {
        'actions': ['pybabel compile -D newbot -d l10n -l eng'],
        'file_dep': [locales_dir],
        'targets': [babel_cfg]
    }


def task_rus():
    """Translate into Russian."""

    def create_cmd_string(x):
        return "echo Succesfully russified!" if x else "echo It has already russified, nothing to do."

    if x := os.path.exists('l10n/eng/LC_MESSAGES/newbot.mo'):
        os.remove('l10n/eng/LC_MESSAGES/newbot.mo')
    return {
        'actions': [CmdAction(create_cmd_string(x))],
        'verbosity': 2,
        }
