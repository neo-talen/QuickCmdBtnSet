# -*- coding:utf-8 -*-
# Author: nelat
# Date  : 2022/4/18
# Note  :
from Core.SingletonMeta import SingletonBase, singleton_it


@singleton_it
class Shell(object):
	def __init__(self):
		self.running = True

	def run(self):
		while self.running:
			op = input('>>>')
			if op == 'quit':
				break
			self.do_something(op)

	def do_something(self, op):
		print(op)


if __name__ == '__main__':
	s = Shell()
	s.run()

