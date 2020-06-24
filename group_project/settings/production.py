from .base import *
import os

debug = False
ALLOWED_HOSTS = ['*']

SECRET_KEY = os.environ('SECRET_KEY')
# 指定收集静态文件的路径
STATIC_ROOT = '/Users/xiaowei/server/django/static'