

# a comparison between top vs all users data for each card, filtered by large
# diffs between the two in all 10 archetypes.
#
# possible: diffs in "all decks" data as well. maybe start with that

import json
from typing import List, Dict
from constants import caliberRequestMap, colorPairs


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
		print(f'{key}')


	for colorPair in colorPairs:
		print(f'\n🌊 colors: {colorPair}')

		pass


displayDiffsByRarity(list('CMUR'))