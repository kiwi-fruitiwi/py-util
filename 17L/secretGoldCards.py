# display large differences in overall vs archetype win rate through various
# metrics: OH, GD, GIH

import json
from typing import List, Dict
from constants import colorPairs, ANSI, loadJson
from cardDisplay import getGrade, gradeBounds, printArchetypesData


def displayArchetypeDiffs(rarityList: List[str]):
	topMaster: Dict = loadJson('data/topMaster.json')
	topStats: Dict = loadJson('data/topStats.json')
	allMaster: Dict = loadJson('data/allMaster.json')
	allStats: Dict = loadJson('data/allStats.json')

	for key, value in allMaster.items():
		print(f'{key}')


displayArchetypeDiffs(list('CMUR'))