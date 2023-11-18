# display large differences in overall vs archetype win rate through various
# metrics: OH, GD, GIH

import json
from typing import List, Dict
from constants import colorPairs, ANSI, loadJson
from cardDisplay import getGrade, gradeBounds, printArchetypesData


def displayArchetypeDiffs(rarityList: List[str]):
	topUsersJsonPath: str = f'data/topMaster.json'
	topStatsJsonPath: str = f'data/topStats.json'

	allUsersJsonPath: str = f'data/allMaster.json'
	allStatsJsonPath: str = f'data/allStats.json'

	with open(topUsersJsonPath, 'r', encoding='utf-8') as jsonFileHandler:
		topMaster: Dict = json.load(jsonFileHandler)

	with open(topStatsJsonPath, 'r', encoding='utf-8') as jsonFileHandler:
		topStats: Dict = json.load(jsonFileHandler)

	with open(allUsersJsonPath, 'r', encoding='utf-8') as jsonFileHandler:
		allMaster: Dict = json.load(jsonFileHandler)

	with open(allStatsJsonPath, 'r', encoding='utf-8') as jsonFileHandler:
		allStats: Dict = json.load(jsonFileHandler)