import requests
from bs4 import BeautifulSoup

import pprint
import time

class Submission:
  def __init__(self, contest_id, epoch_second, execution_time, id, language, length, point, problem_id, result, user_id):
    self.__contest_id = contest_id
    self.__epoch_second = epoch_second
    self.__execution_time = execution_time
    self.__id = id
    self.__language = language
    self.__length = length
    self.__point = point
    self.__problem_id = problem_id
    self.__result = result
    self.__user_id = user_id

class AtcoderUserData:
  def __init__(self, user):
    self.__user = user
    self.__submissions = list()
    self.__fetch()

  def __fetch(self):
    self.__fetch_submissions(0)

  def __fetch_submissions(self, second):
    time.sleep(1)
    data = requests.get(f'https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions?user={self.__user}&from_second={second}').json()

    if len(data) == 0:
      return

    for d in data:
      self.__submissions.append(Submission(**d))
    self.__fetch_submissions(data[-1]['epoch_second'] + 1)

  def get(self):
    return self.__submissions

class Main:
  def __init__(self):
    h = AtcoderUserData('tawainfer')
    print(len(h.get()))

if __name__ == '__main__':
  Main()
