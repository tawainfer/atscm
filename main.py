import requests
from bs4 import BeautifulSoup

import pprint
import time

class SubmissionHistory:
  def __init__(self, user, second = 0):
    self.__user = user
    self.__data = list()
    self.__fetch(second)

  def __fetch(self, second):
    time.sleep(1)
    submissions = requests.get(f'https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions?user={self.__user}&from_second={second}').json()
    self.__data += submissions
    if len(submissions) == 500:
      self.__fetch(submissions[-1]['epoch_second'] + 1)

  def get(self):
    return self.__data

class Main:
  def __init__(self):
    h = SubmissionHistory('tawainfer', 0)
    print(len(h.get()))

if __name__ == '__main__':
  Main()
