# -*- coding:utf-8 -*-
# Author: nelat
# Date  : 2022/4/18
# Note  :


class SingletonBase(object):
	"""
	any class derived this will make it an Singleton class.
	"""
	instance = None

	def __new__(cls, *args, **kwargs):
		if cls.instance is None:
			cls.instance = super(SingletonBase, cls).__new__(cls, *args, **kwargs)
		return cls.instance


def singleton_it(klass):
	'''
	:param cls: cls need tobe singleton
	:return:
	'''
	class NewClass(klass):
		instance = None

		def __new__(cls, *args, **kwargs):
			if cls.instance is None:
				cls.instance = super(NewClass, cls).__new__(cls, *args, **kwargs)
			return cls.instance

	return NewClass


def singleton_it2(klass):
	def new(cls, *args, **kwargs):
		if cls.instance is None:
			cls.instance = klass.__new__(cls, *args, **kwargs)
		return cls.instance

	return type(
		'%s' % klass.__name__,
		(object,),
		{
			'instance': None,
			'__new__': new
		}
	)
