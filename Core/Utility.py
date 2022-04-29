# -*- coding:utf-8 -*-
# Author: nelat
# Date  : 2022/4/28
# Note  :
from Core.Config import IS_DEBUG


def log_warning(msg: str):
	print('WARNING: ', msg)


def log_error(msg: str):
	print('ERROR: ', msg)


def log_info(msg: str):
	print('INFO: ', msg)


def log_log(msg: str):
	if IS_DEBUG:
		print('LOG: ', msg)
