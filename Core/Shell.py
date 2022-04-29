# -*- coding:utf-8 -*-
# Author: nelat
# Date  : 2022/4/18
# Note  :
import os
from Core.SingletonMeta import SingletonBase, singleton_it
from Core.Cmd import CmdsCollection
from Core.Config import DATA_DIR
from Core.Utility import log_info, log_error, log_warning

GLOBAL_CMDS_NAME = 'Global'


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
		self.global_cmds.add_func_cmd('document', lambda: self.help(None, True), '更详细的帮助信息', 'doc')

	def form_input_hint(self):
		return '%s>>>' % self.current_project.name

	def run(self):
		while self.running:
			op = input(self.form_input_hint())
			if op == 'quit':
				break
			self.do_something(op)

	def do_something(self, op):
		cmd_name_or_shortcut, *args = op.split(' ')
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

