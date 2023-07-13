# display a list of top n cards of each color pair with stats
# gihwr, ohwr, iwd, alsa
#
# start with master.json
# 	iterate through keys for the card names?
#
# sort master.json by 'UG GIHWR' using a sorting key
#	take the first n items of a set rarity and display them
import json
from typing import Dict, List
from constants import colorPairs  # WU, UG, WR, etc.
from constants import minimumSampleSize


# this sorting key lets us parameterize color pair and stat
# for example, 'GIH WR' under 'UG' will sort by game-in-hand win rate in the
# colors blue-green
def sortingKey(item, colorPair: str, stat: str):
	key: str = item[0]
	value: Dict = item[1]

	# not all colorPairs exist under 'filteredStats' due to low sample size
	# low sample size colorPair data is simply excluded to save space
	if colorPair in value['filteredStats']:
		colorPairData = value['filteredStats'][colorPair]
		sortingValue = colorPairData[stat]
	else:
		return float('-inf')

	# sometimes the json value is null. this is converted to None in python
	# we want these values to be as infinitely negative as possible so they sort
	# to the end of the list in descending order
	if sortingValue is None:
		# print(f'🐳 {key} is None')
		return float('-inf')

	# sample size needs to be high enough. based this solely on # GIH
	# which is number of game-in-hand, i.e. in opening hand or drawn
	if colorPairData['# GIH'] < minimumSampleSize:
		# print(f'🦈 {key} not enough data: {value[f"{prefix} # GIH"]}')
		return float('-inf')

	return sortingValue


# displays top cards of each colorPair by rarity: 'C', 'U', 'R', 'M'
def displayTopCardsByRarity(rarity: str):
	currentJsonPath: str = f'data/master.json'
	with open(currentJsonPath, 'r', encoding='utf-8') as jsonFileHandler:
		master: Dict = json.load(jsonFileHandler)

	for colorPair in colorPairs:
		print(f'\n🌊 colors: {colorPair}')

		# sort the data per colorPair
		sortingStat: str = 'GIH WR'
		sortedData = dict(
			sorted(
				master.items(),
				key=lambda item: sortingKey(item, colorPair, sortingStat),
				reverse=True
			)
		)

		# take the first n items of a set rarity and display them
		# TODO print stats! → # GIH, GIH WR, OH WR, IWD, zScore, grade
		maxCount: int = 8
		count: int = 0
		for key, value in sortedData.items():
			if value.get("Rarity") == rarity:
				nGih: int = value['filteredStats'][colorPair]['# GIH']
				print(f'{nGih:>5} {key}')
				count += 1

				if count >= maxCount:
					break


displayTopCardsByRarity('C')
