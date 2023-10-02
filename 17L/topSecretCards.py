

# a comparison between top vs all users data for each card, filtered by large
# diffs between the two in all 10 archetypes.
#
# possible: diffs in "all decks" data as well. maybe start with that

import json
from typing import List, Dict
from constants import colorPairs


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
			try:
				allGIHWR: float or None = \
					allMaster[key]['filteredStats'][colorPair]['GIH WR']
			except KeyError:
				allGIHWR = None

			try:
				topGIHWR: float or None = \
					topMaster[key]['filteredStats'][colorPair]['GIH WR']
			except KeyError:
				# sometimes top players don't use a card at all, e.g.
				# eerie interference
				topGIHWR = None

			if allGIHWR and topGIHWR:
				print(f'{key} → all:{allGIHWR}, top:{topGIHWR}')

			pass
		print(f'🐳')


displayDiffsByRarity(list('CMUR'))