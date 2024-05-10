import requests
from requests.adapters import HTTPAdapter
import time

class RequestSession:
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
  def get(cls, url, retry=0, timeout_sec=3):
    time.sleep(1)
    try:
      res = cls.__session.get(url, timeout=timeout_sec)
      res.raise_for_status()
      return res
    except requests.exceptions.RequestException as e:
      if retry >= 1:
        return cls.get(url, retry - 1, timeout_sec * 1.5)

    return None

if __name__ == '__main__':
  pass