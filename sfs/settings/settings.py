# use this file to toggle between dev and production settings

try:
  from .dev import *
except ImportError:
  pass
