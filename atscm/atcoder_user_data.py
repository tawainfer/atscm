import time
from pathlib import Path

import yaml

from .request_session import *
from .submission import *

class AtcoderUserData:
  def __init__(self, user):
    self.__user = user
    self.__submissions = list()
    self.__fetch()

  def __fetch(self):
    self.__fetch_submissions(0)

  def __fetch_submissions(self, second):
    time.sleep(1)
    data = RequestSession().get(f'https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions?user={self.__user}&from_second={second}', 3).json()

    if len(data) == 0:
      return

    for d in data:
      self.__submissions.append(Submission(**d))
    self.__fetch_submissions(data[-1]['epoch_second'] + 1)

  def get_submissions(self):
    return self.__submissions
