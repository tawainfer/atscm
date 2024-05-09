import requests
from bs4 import BeautifulSoup
from pathlib import Path
import re
import git
import yaml
import shutil
import tempfile
import time
from datetime import datetime
from zoneinfo import ZoneInfo
from requests.adapters import HTTPAdapter

class RequestSession():
  __instance = None
  __session = None

  def __new__(cls):
    if not cls.__instance:
      cls.__instance = super(RequestSession, cls).__new__(cls)
      cls.__session = cls.create_session()
    return cls.__instance

  @classmethod
  def create_session(cls):
    session = requests.Session()
    session.mount('https://', HTTPAdapter())
    return session

  @classmethod
  def get(cls, url, retry = 0, timeout_sec = 3):
    time.sleep(1)
    try:
      res = cls.__session.get(url, timeout = timeout_sec)
      res.raise_for_status()
      return res
    except requests.exceptions.RequestException as e:
      if retry >= 1:
        return cls.get(url, retry - 1, timeout_sec * 1.5)

    return None

class LanguageUsedInAtcoder:
  language_to_extension = None

  def __init__(self, language):
    self.__full_name = language
    self.__display_name = re.sub(r'\([^()]*\)', '', self.__full_name).strip()
    self.__version = re.findall(r'\([^()]*\)', self.__full_name)[0].strip('(').strip(')')
    self.__name = self.__display_name.split()[0]

  def get_name(self):
    return self.__name

class Submission:
  language_to_extension = None

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

    self.__extension = self.__identify_extension()
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
  
  def get_result(self):
    return self.__result
  
  def get_extension(self):
    return self.__extension

  def get_url(self):
    return self.__url

  def get_code(self):
    if self.__code is None:
      self.__scripe()
    return self.__code

  def __identify_extension(self):
    if Submission.language_to_extension is None:
      with open(Path(__file__).parent / 'language_to_extension.yaml') as f:
        Submission.language_to_extension = yaml.safe_load(f)

    if self.__language.get_name() in Submission.language_to_extension:
      return Submission.language_to_extension[self.__language.get_name()]
    return None

  def __scripe(self):
    time.sleep(1)
    data = RequestSession().get(self.__url, 3)
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
    data = RequestSession().get(f'https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions?user={self.__user}&from_second={second}', 3).json()

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

  def __del__(self):
    shutil.rmtree(self.__path)

  def get_path(self):
    return self.__path

  def add(self, submissions):
    for s in submissions:
      if s.get_result() != 'AC':
        continue

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
        source_path = problem_path / f'{s.get_problem_id()}.{s.get_extension()}'
        with open(source_path, 'w') as f:
          f.write(s.get_code())

        with open(index_path, 'w') as f:
          yaml.dump(index, f)

  def update(self):
    self.__repo.git.add(self.__path)
    if len(self.__repo.index.diff("HEAD")) == 0:
      print('Already up to date.')
      return
    self.__commit()
    self.__push()

  def __commit(self):
    self.__repo.git.commit('-m', f'update: {datetime.now(ZoneInfo("Asia/Tokyo")).strftime('%Y-%m-%d %H:%M:%S %z')}')

  def __push(self):
    self.__repo.remote().push()

  def __clone(self):
    git.Repo.clone_from(self.__clone_url, self.__path)
    return git.Repo(self.__path)
  
  def __setup(self):
    if 'main' not in self.__repo.branches:
      raise Exception("mainブランチをリモートリポジトリに作成してください。")
    self.__repo.git.checkout('main')

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
