# -*- coding:utf-8 -*-
# Author: nelat
# Date  : 2022/4/18
# Note  :
import sys
from Core.Shell import Shell


if __name__ == '__main__':
	is_gui = False
	if len(sys.argv) > 1 and sys.argv[1] == '-gui':
		is_gui = True

	if not is_gui:
		s = Shell()
		s.run()
