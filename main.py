import requests
from bs4 import BeautifulSoup
from pathlib import Path
import re
import ast
import git
import yaml
import shutil
import tempfile
import time

class LanguageUsedInAtcoder:
  language_list = None

  def __init__(self, language):
    self.__full_name = language
    self.__display_name = re.sub(r'\([^()]*\)', '', self.__full_name).strip()
    self.__version = re.findall(r'\([^()]*\)', self.__full_name)[0].strip('(').strip(')')
    self.__base_name = self.__identify_base_name()

  def __identify_base_name(self):
    if LanguageUsedInAtcoder.language_list is None:
      self.__fetch()

    words = self.__full_name.split()
    for l in LanguageUsedInAtcoder.language_list:
      for w in words:
        if l == w:
          return l
    return None

  def __fetch(self):
    time.sleep(1)
    LanguageUsedInAtcoder.language_list = ast.literal_eval(requests.get(f'https://kenkoooo.com/atcoder/atcoder-api/v3/language_list').text)

class Submission:
  def __init__(self, contest_id, epoch_second, execution_time, id, language, length, point, problem_id, result, user_id):
    self.__contest_id = contest_id
    self.__epoch_second = epoch_second
    self.__execution_time = execution_time
    self.__id = id
    self.__language = LanguageUsedInAtcoder(language)
    self.__length = length
    self.__point = point
    self.__problem_id = problem_id
    self.__result = result
    self.__user_id = user_id

    self.__extension = 'cpp'
    self.__category_id = 'other'
    self.__url = f'https://atcoder.jp/contests/{self.__contest_id}/submissions/{self.__id}'
    self.__code = None

  def get_id(self):
    return self.__id

  def get_language(self):
    return self.__language

  def get_category_id(self):
    return self.__category_id

  def get_contest_id(self):
    return self.__contest_id

  def get_problem_id(self):
    return self.__problem_id
  
  def get_extension(self):
    return self.__extension

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
    self.__path = Path(tempfile.mkdtemp())
    self.__repo = self.__clone()
    self.__setup()

  # def __del__(self):
  #   shutil.rmtree(self.__path)

  def get_path(self):
    return self.__path

  def add(self, submissions):
    for s in submissions:
      problem_path = self.__path / Path(s.get_category_id()) \
        / Path(s.get_contest_id()) / Path(s.get_problem_id())
      if not problem_path.is_dir():
        problem_path.mkdir(parents = True)

      index_path = problem_path / 'index.yaml'
      index = dict()
      if index_path.is_file():
        with open(index_path, 'r') as f:
          index = yaml.safe_load(f)

      if s.get_extension() not in index or s.get_id() > index[s.get_extension()]:
        index[s.get_extension()] = s.get_id()
        source_path = problem_path / f'main.{s.get_extension()}'
        with open(source_path, 'w') as f:
          f.write(s.get_code())

        with open(index_path, 'w') as f:
          yaml.dump(index, f)

  def __clone(self):
    git.Repo.clone_from(self.__clone_url, self.__path)
    return git.Repo(self.__path)
  
  def __setup(self):
    if 'main' not in self.__repo.branches:
      raise Exception("mainブランチをリモートリポジトリに作成してください。")
    self.__repo.git.checkout('main')

class Main:
  def __init__(self):
    aud = AtcoderUserData('tawainfer')
    submissions = aud.get_submissions()

    ar = AtcoderRepo('git@github.com:tawainfer/test-repo-for-atcoder-scm.git')
    ar.add([submissions[0]])
    ar.add([submissions[0]])
    # ar.add(submissions)

if __name__ == '__main__':
  Main()
