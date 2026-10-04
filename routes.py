from utils.yamlworks import readConf
from pathlib import Path
import os

def configRead(section):
    BASE_DIR = Path(__file__).resolve().parent
    config_path = BASE_DIR / "config.yaml"
    wholeconfig = readConf(config_path)
    if not wholeconfig:
        print("config.yaml is empty or not exist.")
        raise FileNotFoundError()
    if section in wholeconfig.keys():
        return wholeconfig.get(section, None)
    else:
        print("Cannot find specified section in config.yaml.")
        return None

from submodules.defaults import defaults
# Default Response Page
from submodules.apis import api
# API Parts
from submodules.gui import guis
# GUI Parts
from submodules.crons import crons
# Crontab Parts
from submodules.output_render import csvrender
# CSV/Json Output