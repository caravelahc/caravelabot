import json

from os import environ
from pathlib import Path

try:
    CONFIG_DIR = Path(environ['XDG_CONFIG_HOME'], 'caravelabot')
except KeyError:
    CONFIG_DIR = Path.home() / '.config' / 'caravelabot'

try:
    with open(CONFIG_DIR / 'config.json') as f:
        config = json.load(f)
except FileNotFoundError:
    config = {}

TOKEN = config['token']
DB_PATH = config.get('db_path', CONFIG_DIR / 'bot.db')
CREATOR_ID = config.get('creator_id', 61407387)
