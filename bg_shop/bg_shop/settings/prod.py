from os import getenv
from pathlib import Path

from .base import *


DEBUG = getenv("DJANGO_DEBUG", "0") == "1"

