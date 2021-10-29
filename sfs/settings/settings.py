# use this file to toggle between dev and production settings

try:
  from .production import * # change .dev to .production in prod
except ImportError:
  pass
