# display large differences in overall vs archetype win rate through various
# metrics: OH, GD, GIH

import json
from typing import List, Dict
from constants import colorPairs, ANSI, loadJson
from cardDisplay import getGrade, gradeBounds, printArchetypesData


def displayArchetypeDiffs(rarityList: List[str], caliber: str):
	targetStat: str = 'GIH WR'
	targetDiff: float = 0.4

	masterJson: Dict = loadJson(f'data/{caliber}Master.json')
	statsJson: Dict = loadJson(f'data/{caliber}Stats.json')

	namesToColorIdentity: Dict = generateNameColorIdentityDict()

	# for each card:
	# 	for each colorPair, check the difference between the win rate in that
	# 	pair vs the win rate in all
	for name, value in masterJson.items():
		colorIdentityList: List[str] = namesToColorIdentity[name]

		# skip cards not of the correct rarity
		if value.get("Rarity") not in rarityList:
			continue

		# skip cards that aren't colorless or mono-colored, since signpost un-
		# commons will obviously be strongest in that color pair
		if len(colorIdentityList) > 1:
			print(f'⛔ skipping {name} →{colorIdentityList}')
			continue

		# grab card win rate data
		allGIHWRz: float or None = getStatValue(masterJson[name], 'all', targetStat, getZScore=True)

		# find z-scores in each colorPair that exceed the 'all' stat
		# save these to a dictionary: 🔑colorPairStr, value: stat value
		# then call cardDisplay.printArchetypeData if the list is nonEmpty, with
		# a header saying how many archetypes the card is a secretGoldCard in.
		successfulColorPairZScores: Dict = {}
		for colorPair in colorPairs:
			colorPairZScore: float or None = getStatValue(masterJson[name], colorPair, 'GIH WR', True)

			# if the target stat exists in this colorPair, check the difference
			if colorPairZScore:
				zscoreDifference: float = colorPairZScore - allGIHWRz
				if zscoreDifference > targetDiff:
					successfulColorPairZScores[colorPair] = zscoreDifference

		if successfulColorPairZScores:
			archetypeDescription: str = '→ best in '

			for colorPairID, zScoreValue in successfulColorPairZScores.items():
				archetypeDescription += f'{ANSI.WHITE.value}{colorPairID}{ANSI.RESET.value} +{zScoreValue:.2f} '

			printArchetypesData(name, masterJson, statsJson, caliber, archetypeDescription)
			print(f'')


# helper method because scryfall json is not keyed by name. generates a dict
# with 🔑cardName, value: colorIdentity. e.g. Restless Anchorage ["U","W"]
def generateNameColorIdentityDict() -> Dict[str, List[str]]:
	scryfallData: Dict = loadJson('data/scryfall.json')
	results: Dict[str, List[str]] = {}

	for card in scryfallData:
		# truncate so we only get the main card's name
		# not MDFC backsides or adventures
		name: str = card['name']
		if '//' in card['name']:
			name = card['name'].split(' // ')[0]

		results[name] = card['color_identity']

	return results


def getStatValue(caliberStats: Dict, colorPair: str, stat: str, getZScore: bool = False) -> float or None:
	"""
	protects against KeyErrors by returning None if key does not have a value

	:param caliberStats: allMaster, topMaster dictionaries
	:param colorPair: one of the 10 color pairs
	:param stat: GIH WR, OH WR, GD WR
	:param getZScore: set to True if we want the z-score of the stat instead of
		the float value of the stat itself
	:return: None, a win rate float, or z-score float
	"""
	try:
		target: Dict = caliberStats['filteredStats'][colorPair]
		result = target['z-scores'][stat] if getZScore else target[stat]
	except KeyError:
		result = None

	return result


# don't run this on imports
if __name__ == '__main__':
	userInput: str = input('caliber rarityList: ')
	inputs: List[str] = userInput.split(' ')
	caliber: str = inputs[0]
	rarityList: List[str] = list(inputs[1].upper())

	displayArchetypeDiffs(rarityList, caliber)