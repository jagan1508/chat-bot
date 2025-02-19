import getpass
import os

from dotenv import load_dotenv

load_dotenv()
def set_env(key: str):
  if key not in os.environ:
    os.environ[key]=getpass.getpass(f"{key}:")