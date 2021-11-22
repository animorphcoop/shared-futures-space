# use this file to toggle between dev and production settings

try:
  from .production import *
except ImportError:
  pass
