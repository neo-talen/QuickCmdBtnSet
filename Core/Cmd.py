# -*- coding:utf-8 -*-
# Author: nelat
# Date  : 2022/4/28
# Note  :
import os
import json
import codecs
from typing import Union
from Core.Utility import log_warning, log_error, log_info, log_log


class CmdBase(object):

	def __init__(self, cmd_name, describe='', quick_shortcut=None):
		self.name = cmd_name
		self.describe = describe
		self.quick_shortcut = quick_shortcut

	def is_customizable(self):
		raise NotImplementedError('Derived Class must select its customizable type.')

	def run(self, *args, **kwargs):
		log_log("RunningCmd: %s." % self.name)

	def get_cmd_type_describe(self):
		raise NotImplementedError

	def __str__(self):
		return '<%s>:%s. %s.' % (self.get_cmd_type_describe(), self.name, self.describe) + \
			((' shortcut: %s' % self.quick_shortcut) if self.quick_shortcut else '')

	def doc(self):
		return str(self)


class LocalFuncCmd(CmdBase):
	''' 本地函数调用 '''
	def __init__(self, func_name, desc='', func=None, quick_shortcut=None):
		super(LocalFuncCmd, self).__init__(func_name, desc, quick_shortcut)
		self.func = func

	def is_customizable(self):
		return False

	def run(self, *args, **kwargs):
		super(LocalFuncCmd, self).run()
		self.func and self.func(*args, **kwargs)

	def doc(self):
		base = super(LocalFuncCmd, self).doc()
		return '\n'.join([base, 'function doc required' if self.func.__doc__ is None else self.func.__doc__])

	def get_cmd_type_describe(self):
		return 'build-in'


class SystemCmd(CmdBase):
	''' os.system to call outer executable running '''
	def __init__(self, name='no_name', desc='', work_dir='no_dir', op_cmd='no_op', args=None, quick_shortcut=None):
		'''
		:param work_dir: 指令工作目录
		:param op_cmd: 指令运行程序名
		:param args: 指令运行参数
		'''
		super(SystemCmd, self).__init__(name, desc, quick_shortcut)
		self.work_dir, self.op_cmd, self.args = work_dir, op_cmd, args if args is not None else []

	def is_customizable(self):
		return True

	def run(self, *args, **kwargs):
		super(SystemCmd, self).run()
		old_dir = os.getcwd()
		os.chdir(self.work_dir)
		os.system(' '.join([self.op_cmd] + self.args))
		os.chdir(old_dir)

	def to_dict(self):
		return {
			'name': self.name,
			'desc': self.describe,
			'quick_shortcut': self.quick_shortcut,
			'work_dir': self.work_dir,
			'op_cmd': self.op_cmd,
			'args': self.args
		}

	@staticmethod
	def from_dict(dic):
		self = SystemCmd()
		self.name = dic['name']
		self.describe = dic['desc']
		self.quick_shortcut = dic['quick_shortcut']
		self.work_dir = dic['work_dir']
		self.op_cmd = dic['op_cmd']
		self.args = dic['args']
		return self

	def get_cmd_type_describe(self):
		return 'user-defined'


def dirty_op(func):
	def wrapper(*args, **kwargs):
		obj = args[0]
		obj.dirty = True
		return func(*args, **kwargs)
	wrapper.__doc__ = func.__doc__  # 赋值doc，因为doc会用于显示
	return wrapper


class CmdsCollection(object):
	FILE_SUFFIX = 'cmds'

	def __init__(self, name='None', no_default_func_cmds=False):
		self.name = name
		self.cmds = {}  # {cmd_name: cmd}  需要运行外部程序的cmds
		self.quick_shortcut_to_cmd = {}  # 快捷指令
		self.is_dirty = False  # 是否有改动

		if not no_default_func_cmds:
			self.add_func_cmd('add_cmd', self.add_system_cmd, '为当前命令集合新增一个命令', 'ac')
			self.add_func_cmd('remove_cmd', self.remove_cmd, '移除某个命令', 'rc')
			self.add_func_cmd('help', lambda: self.help(None, False), '简单的列出可选指令', 'h')
			self.add_func_cmd('list_cmds', lambda: self.help(None, False), '简略帮助信息', 'ls')
			self.add_func_cmd('document', lambda: self.help(None, True), '详细的列出指令参数信息', 'doc')
			self.add_func_cmd('change_shortcut', self.change_shortcut, '修改快捷指令字符', 'cs')

	# def disable_cmd(self, cmd_name):
	# 	''' 关闭某些指令功能, 包括无法运行和help不显示帮助文档 '''
	# 	self.disabled_cmd_names.add(cmd_name)

	def set_fixed(self, cmd_name):
		''' make a cmd not customizable '''
		pass

	def __bool__(self):
		return self.name != 'None'

	def _check_cmd_valid(self, cmd):
		if cmd.name in self.cmds:
			log_error('Cmd named: <%s> already registered.\n%s' % (cmd.name, cmd))
			return False
		elif cmd.quick_shortcut in self.quick_shortcut_to_cmd:
			log_error('Cmd\'s quick shortcut: <%s> already registered.\n%s' % (cmd.quick_shortcut, cmd))
			return False
		return True

	def add_func_cmd(self, func_name, func, desc, quick_shortcut=None):
		self.__add_cmd(LocalFuncCmd(func_name, desc, func, quick_shortcut))

	@dirty_op
	def add_system_cmd(self):
		"""
		添加指令
		参数： 指令名称，指令描述，指令工作目录，指令可执行文件名称，执行参数，指令的快捷字符
		:return: 
		"""

		arg_list = [
			'name', 'desc', 'work_dir', 'op_cmd', 'args', 'quick_shortcut'
		]
		arg_describe = {
			'name': '指令名称',
			'desc': '指令描述',
			'work_dir': '指令工作目录',
			'op_cmd': '指令可执行文件名称',
			'args': '执行参数',
			'quick_shortcut': '指令的快捷字符',
		}
		arg_input = {}
		for arg_name in arg_list:
			arg_input[arg_name] = input(arg_describe[arg_name] + ': ')
			if arg_name == 'args':
				arg_input[arg_name] = arg_input[arg_name].split(' ')

		self.__add_cmd(SystemCmd(*[arg_input[x] for x in arg_list]))

	def __add_cmd(self, cmd):
		if self._check_cmd_valid(cmd):
			self.cmds[cmd.name] = cmd
			if cmd.quick_shortcut:
				self.quick_shortcut_to_cmd[cmd.quick_shortcut] = cmd
			log_log('AddCmd Successed.')
		else:
			log_log('AddCmd Failed.')

	def change_shortcut(self, cmd_name, new_shortcut):
		"""
		修改快捷指令字符
		:param cmd_name: 待修改的指令名称
		:param new_shortcut: 新的快捷指令字符
		:return:
		"""
		if cmd_name in self.cmds:
			if new_shortcut in self.quick_shortcut_to_cmd:
				log_error('ChangeShorcut: Failed for new shortcut:%s already exist.' % new_shortcut)
			else:
				cmd = self.cmds[cmd_name]
				if not cmd.is_customizable():
					log_error('ChangeShortcut: Failed for cmd: %s is not customizable.' % cmd_name)
					return
				if cmd.quick_shortcut in self.quick_shortcut_to_cmd:
					del self.quick_shortcut_to_cmd[cmd.quick_shortcut]
				self.quick_shortcut_to_cmd[new_shortcut] = cmd
				cmd.quick_shortcut = new_shortcut
		else:
			log_error('ChangeShortcut: Failed for cmd: %s not exist.' % cmd_name)

	@dirty_op
	def remove_cmd(self, cmd_name):
		"""
		移除指令
		:param cmd_name: 指令名称
		:return:
		"""
		if cmd_name in self.cmds:
			cmd = self.cmds[cmd_name]
			if not cmd.is_customizable():
				log_error('RemoveCmd: failed because try to remove fixed cmd: %s' % cmd)
				return
			del self.cmds[cmd_name]
			if cmd.quick_shortcut:
				del self.quick_shortcut_to_cmd[cmd.quick_shortcut]
			log_log('RemoveCmd: Successed.')
		else:
			log_log('RemoveCmd: cmd_name not exist.')

	def _get_cmd_by_name_or_shorcut(self, cmd_name_or_shortcut):
		cmd = self.quick_shortcut_to_cmd.get(cmd_name_or_shortcut, None)
		if cmd is None:
			cmd = self.cmds.get(cmd_name_or_shortcut, None)
		return cmd

	def run_cmd(self, cmd_name_or_shortcut, *args, **kwargs):
		log_log('Running in collection: %s' % self.name)
		cmd = self._get_cmd_by_name_or_shorcut(cmd_name_or_shortcut)
		if cmd:
			try:
				cmd.run(*args, **kwargs)
			except Exception as e:
				log_error(str(e))
		else:
			log_info('Cmd:%s not found.' % cmd_name_or_shortcut)

	def help(self, cmd_name_or_short_cut=None, use_doc=False):
		"""
		帮助信息
		:param cmd_name_or_short_cut: 指定指令名称
		:param use_doc: 带参数信息的帮助信息
		:return:
		"""
		if cmd_name_or_short_cut is None:
			# print all info
			for cmd_name, cmd in self.cmds.items():
				cmd_info = cmd.doc() if use_doc else str(cmd)
				log_info('<Project: %s>: %s.' % (self.name, cmd_info))
		else:
			cmd = self._get_cmd_by_name_or_shorcut(cmd_name_or_short_cut)
			if cmd:
				cmd_info = cmd.doc() if use_doc else str(cmd)
				log_info('<Project: %s>: %s.' % (self.name, cmd_info))
			else:
				log_info('<Project: %s>: %s not found.' % (self.name, cmd_name_or_short_cut))

	def __contains__(self, item):
		return bool(self._get_cmd_by_name_or_shorcut(item))

	@staticmethod
	def form_file_path(name, data_dir):
		return os.path.join(data_dir, '%s.%s' % (name, CmdsCollection.FILE_SUFFIX))

	def dump_to(self, file_dir):
		dump_dict = {
			'name': self.name,
			'cmds': {cmd_name: cmd.to_dict() for cmd_name, cmd in self.cmds.items() if cmd.is_customizable()},
		}
		with open(self.form_file_path(self.name, file_dir), 'w', encoding='utf-8') as fp:
			json.dump(dump_dict, fp, indent=4, ensure_ascii=False)

	def load_from(self, file_dir):
		file_path = self.form_file_path(self.name, file_dir)
		if not os.path.exists(file_path):
			log_warning('file<%s> not exist.' % file_path)
			return
		with open(file_path, 'r', encoding='utf-8') as fp:
			info = json.load(fp)
			self.name = info['name']
			self.cmds.update({cmd_name: SystemCmd.from_dict(cmd_info) for cmd_name, cmd_info in info['cmds'].items()})
			self.quick_shortcut_to_cmd = {cmd.quick_shortcut: cmd for _, cmd in self.cmds.items() if cmd.quick_shortcut}
