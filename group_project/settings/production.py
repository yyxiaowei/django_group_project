from .base import *
import os

debug = False
ALLOWED_HOSTS = ['*']

SECRET_KEY = os.environ('SECRET_KEY')
