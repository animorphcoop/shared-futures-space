# use this file to toggle between dev and production settings

try:
  from .dev import * # change .dev to .production in prod
except ImportError:
  pass
