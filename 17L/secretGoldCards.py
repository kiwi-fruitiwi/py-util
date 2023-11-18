# display large differences in overall vs archetype win rate through various
# metrics: OH, GD, GIH

import json
from typing import List, Dict
from constants import colorPairs, ANSI, loadJson
from cardDisplay import getGrade, gradeBounds, printArchetypesData


def displayArchetypeDiffs(rarityList: List[str]):
	targetStat: str = 'GIH WR'
	targetDiff: float = 0.5

	topMaster: Dict = loadJson('data/topMaster.json')
	topStats: Dict = loadJson('data/topStats.json')
	allMaster: Dict = loadJson('data/allMaster.json')
	allStats: Dict = loadJson('data/allStats.json')

	# for each card:
	# 	for each colorPair, check the difference between the win rate in that
	# 	pair vs the win rate in all
	for name in allMaster.keys():
		# grab card win rate data
		allGIHWRz: float or None = getStatValue(allMaster[name], 'all', 'GIH WR', True)

		# find z-scores in each colorPair that exceed the 'all' stat
		# save these to a dictionary: 🔑colorPairStr, value: stat value
		# then call cardDisplay.printArchetypeData if the list is nonEmpty, with
		# a header saying how many archetypes the card is a secretGoldCard in.
		successfulColorPairZScores: Dict = {}
		for colorPair in colorPairs:
			colorPairZScore: float or None = getStatValue(allMaster[name], colorPair, 'GIH WR', True)

			# if the target stat exists in this colorPair, check the difference
			if colorPairZScore:
				zscoreDifference: float = colorPairZScore - allGIHWRz
				if zscoreDifference > targetDiff:
					successfulColorPairZScores[colorPair] = zscoreDifference

		if successfulColorPairZScores:
			print(f'{name} ', end='')
			for key, value in successfulColorPairZScores.items():
				print(f'{key} +{value:.2f} ', end='')
			print(f'')



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


displayArchetypeDiffs(list('CU'))