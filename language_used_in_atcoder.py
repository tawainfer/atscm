import re

class LanguageUsedInAtcoder:
  def __init__(self, language):
    self.__full_name = language
    self.__display_name = re.sub(r'\([^()]*\)', '', self.__full_name).strip()
    self.__version = re.findall(r'\([^()]*\)', self.__full_name)[0].strip('(').strip(')')
    self.__name = self.__display_name.split()[0]

  def get_name(self):
    return self.__name
