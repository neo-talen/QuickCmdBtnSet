# -*- coding:utf-8 -*-
# Author: nelat
# Date  : 2022/4/28
# Note  :
from Core.Config import IS_DEBUG


def log_warning(msg):
	print('WARNING: ', msg)


def log_error(msg):
	print('ERROR: ', msg)


def log_info(msg):
	print('INFO: ', msg)


def log_log(msg):
	if IS_DEBUG:
		print('LOG: ', msg)


class FixedLengthList(object):
	def __init__(self, max_limit=50):
		self.max_limit = max_limit
		self.write_idx = 0  # list满的时候写入的索引
		self.cache = []

	def __len__(self):
		return len(self.cache)

	def is_full(self):
		return len(self.cache) == self.max_limit

	def append(self, item):
		if not self.is_full():
			self.cache.append(item)
			self.write_idx += 1
		else:
			self.cache[self.write_idx] = item
			self.write_idx += 1
			self.write_idx = self.write_idx % self.max_limit

	def read_forward(self, offset):
		if offset <= 0:
			return None
		idx = (self.write_idx - offset) % len(self.cache)
		return self.cache[idx]

	def __contains__(self, item):
		return item in self.cache
