# -*- coding:utf-8 -*-
# Author: nelat
# Date  : 2022/4/18
# Note  :
import os
import json
from typing import List
from Core.Config import DATA_DIR, COLLECTIONS_INFO_PATH
from Core.Cmd import CmdsCollection


def write_collections_info(collections: List[CmdsCollection]):
	with open(COLLECTIONS_INFO_PATH, 'w') as fp:
		json.dump({p.name: p.to_dict for p in collections}, fp)


def read_collections_info() -> List[CmdsCollection]:
	with open(COLLECTIONS_INFO_PATH, 'r') as fp:
		collections_info = json.load(fp)
		return [
			CmdsCollection().from_dict(dic) for collection_name, dic in collections_info.items()
		]

