#!/usr/bin/env python
import os
import sys
from django.conf import settings

if __name__ == "__main__":
    if settings.DEBUG:
      os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sfs.settings.dev")
    else:
      os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sfs.settings.production")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
