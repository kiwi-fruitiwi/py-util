# display a list of top n cards of each color with stats
# gihwr, ohwr, gdwr, iwd, alsa
import json
from typing import Dict, List
from constants import minGihSampleSize, caliberRequestMap, loadJson
from cardDisplay import printCardComparison


# this sorting key lets us parameterize the stat, e.g. GDWR OHWR GIHWR
def statSortingKey(item, stat: str):
	value: Dict = item[1]  # item[0] is the 🔑
	allData: dict = value['filteredStats']['all']
	sortingValue: float = allData[stat]

	# sometimes the json value is null. this is converted to None in python
	# we want these values to be as infinitely negative as possible so they sort
	# to the end of the list in descending order
	if sortingValue is None:
		return float('-inf')

	# sample size needs to be high enough. based this solely on # GIH
	# which is number of game-in-hand, i.e. in opening hand or drawn
	if allData['# GIH'] < minGihSampleSize:
		return float('-inf')

	return sortingValue


# displays top n cards of each colorPair by rarity: 'C', 'U', 'R', 'M'
def displayTopCardsInEachColorByRarity(
		rarityList: List[str], cardsToDisplay: int, includeMulticolor=True):

	# go through colors and iterate through calibers in each
	for color in 'WUBRG':
		print(f'\n🌊 color: {color}')

		for caliber in caliberRequestMap.keys():
			master: Dict = loadJson(f'data/{caliber}Master.json')

			# sorting the data must come before iterating because we take the
			# -first- n entries that satisfy our color and rarity requirements
			# below. not sorting misses possibilities at the end of the json
			sortingStat: str = 'OH WR'
			sortedData = dict(
				sorted(
					master.items(),
					key=lambda item: statSortingKey(item, sortingStat),
					reverse=True
				)
			)

			# take the first n sorted-by-stat items of a rarity and display them
			maxCount: int = cardsToDisplay
			count: int = 0
			cardFetchList: List[str] = []

			for name, cardData in sortedData.items():
				if cardData.get("Rarity") in rarityList:

					# we can either use 'color in' to include multicolor cards
					# or 'color ==' to restrict only monocolor ones
					filterClause: bool
					if includeMulticolor:
						filterClause = color in cardData.get("Color")
					else:
						filterClause = (color == cardData.get("Color"))

					if filterClause:
						nGih: int = cardData['filteredStats']['all']['# GIH']
						if nGih > minGihSampleSize:
							cardFetchList.append(name)
						count += 1

						if count >= maxCount:
							break

			printCardComparison(cardFetchList, 'all', caliber)
			print()


# don't run this on imports
if __name__ == '__main__':
	# display default setting: top 12 commons + uncommons
	displayTopCardsInEachColorByRarity(['C', 'U'], 10, includeMulticolor=False)

	# ask user what settings they want
	print(f'lack of sample size for top caliber players will put commons and uncommons at the top of the list')
	userInput: str = input('n rarityList: ')
	inputs: List[str] = userInput.split(' ')
	n: int = int(inputs[0])
	rarity: List[str] = list(inputs[1].upper())
	displayTopCardsInEachColorByRarity(rarity, n, includeMulticolor=True)
