from bs4 import BeautifulSoup
from pathlib import Path
import re
import time
import yaml
from request_session import RequestSession
from language_used_in_atcoder import LanguageUsedInAtcoder

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
