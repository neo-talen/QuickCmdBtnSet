# -*- coding:utf-8 -*-
# Author: nelat
# Date  : 2022/4/18
# Note  :
from Core.SingletonMeta import singleton_it


class SingleCmd(object):
	''' 单条指令 '''
	__slots__ = ['work_dir', 'op_cmd', 'args']

	def __init__(self, work_dir, op_cmd, args):
		'''
		:param work_dir: 指令工作目录
		:param op_cmd: 指令运行程序名
		:param args: 指令运行参数
		'''
		self.work_dir, self.op_cmd, self.args = work_dir, op_cmd, args


def run_a_cmd(cmd: SingleCmd):
	print(cmd)


if __name__ == '__main__':
	run_a_cmd(SingleCmd(1, 2, 3))
