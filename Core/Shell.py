# -*- coding:utf-8 -*-
# Author: nelat
# Date  : 2022/4/18
# Note  :
import sys
import os
import keyboard
from Core.SingletonMeta import SingletonBase, singleton_it
from Core.Cmd import CmdsCollection
from Core.Config import DATA_DIR
from Core.Utility import log_info, log_error, log_warning, FixedLengthList


GLOBAL_CMDS_NAME = 'Global'


class InputHandler(object):
	"""
	管理所有的输入，以enter键作为结束一次输入的返回
	"""
	def __init__(self):
		self.inputs = ''

	def on_press(self, key):
		pass

	def fetch_one(self):
		pass


@singleton_it
class Shell(object):
	def __init__(self):
		self.running = True
		self.global_cmds = CmdsCollection(GLOBAL_CMDS_NAME, True)  # 全局的命令
		# self.global_cmds.load_from(DATA_DIR)
		log_info('Shell Initialized...')
		self.current_project = self.global_cmds
		self.project_names = [file_name[:-len(CmdsCollection.FILE_SUFFIX) - 1] for file_name in os.listdir(DATA_DIR)]

		self.global_cmds.add_func_cmd('create_project', self.create_project, '创建一个命令集', 'cp')
		self.global_cmds.add_func_cmd('load_project', self.load_project, '加载指定项目的命令集', 'lp')
		self.global_cmds.add_func_cmd('dump_project', self.dump_current_project, '保存当前项目的命令集', 'dump')
		self.global_cmds.add_func_cmd('list_project', self.list_projects, '列出所有可用的项目', 'list')
		self.global_cmds.add_func_cmd('switch_project', self.switch_project, '切换到指定项目', 'sp')
		self.global_cmds.add_func_cmd('delete_project', self.delete_project, '删除指定项目', 'dp')
		self.global_cmds.add_func_cmd('help', self.help, '简略帮助信息', 'h')
		self.global_cmds.add_func_cmd('list_cmds', self.help, '简略帮助信息', 'ls')
		self.global_cmds.add_func_cmd('document', lambda: self.help(None, True), '更详细的帮助信息', 'doc')
		self.global_cmds.add_func_cmd('quit', self.quit_shell, '关闭shell', 'q')

		self.history_inputs = FixedLengthList()
		self.history_travel_offset = 0

	def add_to_history(self, inputs):
		self.history_inputs.append(inputs)

	def read_from_history(self, offset):
		if offset > len(self.history_inputs):
			return None
		return self.history_inputs.read_forward(offset)

	def form_input_hint(self):
		return '%s>>>' % self.current_project.name

	def run(self):

		keyboard.add_hotkey('up', self.on_hotkey_up)
		keyboard.add_hotkey('down', self.on_hotkey_down)
		keyboard.add_hotkey('tab', self.on_hotkey_tab)

		while self.running:
			# input()
			inputs = input(self.form_input_hint())
			self.do_something(inputs)
			self.add_to_history(inputs)
			self.clear_states()

	def clear_states(self):
		self.history_travel_offset = 1

	def on_hotkey_tab(self):
		pass

	def on_hotkey_up(self):
		self.history_travel_offset += 1
		history = self.read_from_history(self.history_travel_offset)
		if history:
			sys.stdout.flush()
			print(history + '\r')

	def on_hotkey_down(self):
		if self.history_travel_offset > 0:
			self.history_travel_offset -= 1
		history = self.read_from_history(self.history_travel_offset)
		if history:
			sys.stdout.flush()
			print(history + '\r')

	def refresh_input(self, msg):
		sys.stdout.flush()

	def write_input(self, msg):
		print('yoyo')

	def do_something(self, inputs):
		splited_inputs = inputs.split(' ')
		cmd_name_or_shortcut = splited_inputs[0]
		args = splited_inputs[1:]
		if self.current_project != self.global_cmds:
			if cmd_name_or_shortcut in self.current_project:
				self.current_project.run_cmd(cmd_name_or_shortcut, *args)
				return

		if cmd_name_or_shortcut in self.global_cmds:
			self.global_cmds.run_cmd(cmd_name_or_shortcut, *args)
		elif cmd_name_or_shortcut in self.project_names:
			self.switch_project(cmd_name_or_shortcut)
		else:
			log_error('cmd: <%s> not exist.' % cmd_name_or_shortcut)

	def yes_or_no(self, msg):
		i = input(msg + ' y/n: ')
		return i == 'y'

	"""----shell global operations"""
	def quit_shell(self):
		log_info('Quit Shell. Goodbye.')
		self.running = False

	def create_project(self, project_name):
		"""
		创建一个项目
		:param project_name: 项目名称
		:return:
		"""
		if project_name in self.project_names:
			log_warning('project: %s already exist.' % project_name)
			if self.current_project.name != project_name:
				self.switch_project(project_name)
		elif project_name == GLOBAL_CMDS_NAME:
			log_error('project name: <%s> is reserved by this application.' % GLOBAL_CMDS_NAME)
		else:
			self.current_project = CmdsCollection(project_name)
			self.dump_current_project()

	def dump_current_project(self):
		"""
		保存当前项目
		:return:
		"""
		if self.current_project.name == GLOBAL_CMDS_NAME:
			log_warning('can not dump global project.')
		else:
			self.current_project.dump_to(DATA_DIR)
			self._refresh_project_names()

	def load_project(self, project_name):
		"""
		加载某个项目
		:param project_name: 项目名称
		:return:
		"""
		if project_name == self.current_project.name:
			log_warning('current project already loaded.')
			return

		if self.current_project.name == GLOBAL_CMDS_NAME:
			pass
		elif self.current_project.is_dirty and self.yes_or_no('save current project:<%s> before load.' % self.current_project.name):
			self.dump_current_project()

		self.current_project = CmdsCollection(project_name)
		self.current_project.load_from(DATA_DIR)

	def _refresh_project_names(self):
		self.project_names = [file_name[:-len(CmdsCollection.FILE_SUFFIX) - 1] for file_name in os.listdir(DATA_DIR)]

	def list_projects(self):
		"""
		列出当前可选的项目
		:return:
		"""
		for name in self.project_names:
			print('project: %s' % name)

	def switch_project(self, project_name=None):
		"""
		切换到指定项目
		:param project_name: 项目名称
		:return:
		"""
		if project_name == self.current_project.name:
			log_warning('already is current project.')
		elif project_name is not None and project_name not in self.project_names:
			log_warning('project name:%s \' config file not exist.' % project_name)
		else:
			if self.current_project.name == GLOBAL_CMDS_NAME:
				pass
			elif self.current_project.is_dirty and self.yes_or_no('save current project:<%s> before switch.' % self.current_project.name):
				self.dump_current_project()

			if project_name is None:
				self.current_project = self.global_cmds
			else:
				self.current_project = CmdsCollection(project_name)
				self.current_project.load_from(DATA_DIR)

	def delete_project(self, project_name):
		"""
		删除指定项目
		:param project_name: 项目名称
		:return:
		"""
		if project_name == GLOBAL_CMDS_NAME:
			log_warning('can not delete global project.')
		if project_name == self.current_project.name:
			if self.yes_or_no('delete current project?'):
				self.current_project = self.global_cmds
		file_path = CmdsCollection.form_file_path(project_name, DATA_DIR)
		os.remove(file_path)
		self._refresh_project_names()

	def help(self, specified_cmd_name_or_shortcut=None, use_doc=False):
		"""
		帮助信息
		:param specified_cmd_name_or_shortcut: 指令名称或快捷名称
		:param use_doc: 是否打印更详细的参数信息
		:return:
		"""
		self.global_cmds.help(specified_cmd_name_or_shortcut, use_doc)
		if self.current_project != self.global_cmds:
			self.current_project.help(specified_cmd_name_or_shortcut, use_doc)


if __name__ == '__main__':
	s = Shell()
	s.run()

