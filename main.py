import tomllib
from pathlib import Path

import yaml

import atscm

class Main:
  def __init__(self):
    config = dict()
    with open(Path(__file__).parent / 'config.toml', 'rb') as f:
      config = tomllib.load(f)

    aud = atscm.UserData(config['atcoder_username'])
    ar = atscm.Repo(config['clone_url'], config['classification'])
    ar.add(aud.get_submissions())
    ar.update()

if __name__ == '__main__':
  Main()
