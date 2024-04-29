import requests
from bs4 import BeautifulSoup
import os
import git
import tempfile
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

    self.__url = f'https://atcoder.jp/contests/{self.__contest_id}/submissions/{self.__id}'
    self.__code = None

  def get_id(self):
    return self.__id

  def get_url(self):
    return self.__url

  def get_code(self):
    if self.__code is None:
      self.__scripe()
    return self.__code

  def __scripe(self):
    time.sleep(1)
    data = requests.get(self.__url)
    html = BeautifulSoup(data.text, 'html.parser')
    element = html.select_one('#submission-code')
    lines = element.text.replace('\r\n', '\n').split('\n')
    self.__code = '\n'.join(lines)

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

  def get_submissions(self):
    return self.__submissions

class AtcoderRepo:
  def __init__(self, clone_url):
    self.__clone_url = clone_url
    self.__path = tempfile.mkdtemp()
    self.__repo = self.__clone()
    self.__setup()

  def __del__(self):
    os.removedirs(self.__path)

  def get_path(self):
    return self.__path

  def __clone(self):
    git.Repo.clone_from(self.__clone_url, self.__path)
    return git.Repo()
  
  def __setup(self):
    if not any(branch.name == 'main' for branch in self.__repo.branches):
      self.__repo.git.add(self.__path)
      self.__repo.git.commit('-m', 'Initial commit')

class Main:
  def __init__(self):
    ar = AtcoderRepo()
    print(ar.get_path())

if __name__ == '__main__':
  Main()
