import shutil
import tempfile
import yaml
import git
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from .request_session import *
from .submission import *

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
        problem_path.mkdir(parents=True)

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
    self.__repo.git.commit('-m', f'update: {datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y-%m-%d %H:%M:%S %z")}')

  def __push(self):
    self.__repo.remote().push()

  def __clone(self):
    git.Repo.clone_from(self.__clone_url, self.__path)
    return git.Repo(self.__path)

  def __setup(self):
    if 'main' not in self.__repo.branches:
      raise Exception("mainブランチをリモートリポジトリに作成してください。")
    self.__repo.git.checkout('main')
