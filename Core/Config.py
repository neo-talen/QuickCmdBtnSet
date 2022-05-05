# -*- coding:utf-8 -*-
# Author: nelat
# Date  : 2022/4/28
# Note  : 
import os

WORK_DIR = os.getcwd()

DATA_DIR = os.path.join(WORK_DIR, 'Data')

if not os.path.exists(DATA_DIR):
	os.mkdir(DATA_DIR)

COLLECTIONS_INFO_PATH = os.path.join(DATA_DIR, 'collections_info.json')

IS_DEBUG = False
