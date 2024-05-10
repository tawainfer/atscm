from pathlib import Path

import yaml

from atscm import AtcoderUserData
from atscm import AtcoderRepo

class Main:
  def __init__(self):
    user_config = dict()
    with open(Path(__file__).parent / 'user_config.yaml') as f:
      user_config = yaml.safe_load(f)

    aud = AtcoderUserData(user_config['atcoder_username'])
    ar = AtcoderRepo(user_config['clone_url'])
    ar.add(aud.get_submissions())
    ar.update()

if __name__ == '__main__':
  Main()
