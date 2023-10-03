

# a comparison between top vs all users data for each card, filtered by large
# diffs between the two in all 10 archetypes.
#
# possible: diffs in "all decks" data as well. maybe start with that

import json
from typing import List, Dict
from constants import colorPairs
from cardDisplay import getGrade, gradeBounds


# displays cards that have a large diff between (all users, top users) by rarity
def displayDiffsByRarity(rarityList: List[str]):
	# assume there's only top and allUsers data. no need to parameterize by
	# caliberRequestMap

	topUsersJsonPath: str = f'data/topMaster.json'
	allUsersJsonPath: str = f'data/allMaster.json'

	with open(topUsersJsonPath, 'r', encoding='utf-8') as jsonFileHandler:
		topMaster: Dict = json.load(jsonFileHandler)

	with open(allUsersJsonPath, 'r', encoding='utf-8') as jsonFileHandler:
		allMaster: Dict = json.load(jsonFileHandler)

	# assume the keys are identical in both topMaster and allMaster json files
	for key, value in allMaster.items():
		# print(f'{key}')
		pass

	for colorPair in colorPairs:
		print(f'\n🌊 colors: {colorPair}')

		# print OH and GD win rates across both calibers per color pair
		# 	value['filteredStats'][colorPair]['# GIH']

		for key in allMaster.keys():
			print(f'{key}')

			# extract win rates by key; note dictionaries keyed by card name
			# sometimes top players don't use a card at all, e.g. eerie
			# interference, so we must check for null values in the json
			#
			# other times, certain archetypes just have no data
			allGIHWRz: float or None = getStatValue(allMaster[key], colorPair, 'GIH WR', True)
			topGIHWRz: float or None = getStatValue(topMaster[key], colorPair, 'GIH WR', True)

			if allGIHWRz and topGIHWRz:
				print(f'{key} → all:{getGrade(allGIHWRz)}, top:{getGrade(topGIHWRz)}')

			pass
		print(f'🐳')


def getStatValue(caliberStats: Dict, colorPair: str, stat: str, getZScore: bool = False) -> float or None:
	"""

	:param caliberStats:
	:param colorPair:
	:param stat:
	:param getZScore:
	:return:
	"""
	try:
		target: Dict = caliberStats['filteredStats'][colorPair]
		result = target['z-scores'][stat] if getZScore else target[stat]
	except KeyError:
		result = None

	return result


displayDiffsByRarity(list('CMUR'))