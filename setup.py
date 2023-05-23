from setuptools import setup, find_packages

setup(
name="QuizerBot",
version="0.1.0",
url="https://github.com/Zenoro/quizer-tg",
author=["Voronets Vladimir","Kirill Tearo"],
author_email=["","kir.tearo@yandex.ru"],
description="Telegram bot for answering tasks",
packages=['QuizerBot'],
entry_points={
        'console_scripts': [
            'QuizerBot = QuizerBot:main',
        ]
    },
install_requires=["telebot","doit"],
extras_require={'dev': ['pytest','flake8','sphinx','babel']},
python_requires='>=3.10',
package_data = {'': ['**/*.po']},
)
