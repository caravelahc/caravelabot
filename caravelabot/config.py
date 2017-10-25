import json
from os import environ
from pathlib import Path


try:
    CONFIG_DIR = Path(environ['XDG_CONFIG_HOME'], 'caravelabot')
except KeyError:
    CONFIG_DIR = Path(environ['HOME'], '.config', 'caravelabot')


def load():
    with open(CONFIG_DIR / 'config.json') as f:
        return json.load(f)


def save(c):
    with open(CONFIG_DIR / 'config.json', 'w') as f:
        json.dump(c, f)
