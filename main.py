from pathlib import Path

import yaml

import atscm

class Main:
  def __init__(self):
    user_config = dict()
    with open(Path(__file__).parent / 'user_config.yaml') as f:
      user_config = yaml.safe_load(f)

    aud = atscm.UserData(user_config['atcoder_username'])
    ar = atscm.Repo(user_config['clone_url'])
    ar.add(aud.get_submissions()[:20])
    ar.update()

if __name__ == '__main__':
  Main()
