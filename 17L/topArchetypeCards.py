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
# for example, 'UG GIH WR' will sort by game-in-hand win rate in blue-green
def sortingKey(item, colorPair: str, stat: str):
	key: str = item[0]
	value: Dict = item[1]

	sortingValue = value[f'{colorPair} {stat}']

	if sortingValue is None:
		# print(f'🐳 {key} is None')
		return float('-inf')

	# sample size needs to be high enough. based this solely on # GIH
	# which is number of game-in-hand, i.e. in opening hand or drawn
	if value[f'{colorPair} # GIH'] < minimumSampleSize:
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

		# sort the data by GIH WR per colorPair
		sortedData = dict(
			sorted(
				master.items(),
				key=lambda item: sortingKey(item, colorPair, 'OH WR'),
				reverse=True
			)
		)

		# take the first n items of a set rarity and display them
		# TODO print stats! → # GIH, GIH WR, OH WR, IWD, zScore, grade
		maxCount: int = 5
		count: int = 0
		for key, value in sortedData.items():
			if value.get("Rarity") == rarity:
				print(key)
				count += 1

				if count >= maxCount:
					break


displayTopCardsByRarity('C')
