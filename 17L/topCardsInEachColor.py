# display a list of top n cards of each color with stats
# gihwr, ohwr, gdwr, iwd, alsa
import json
from typing import Dict, List
from constants import minGihSampleSize, caliberRequestMap

from cardDisplay import printCardComparison


# displays top cards of each colorPair by rarity: 'C', 'U', 'R', 'M'
def displayTopCardsInEachColorByRarity(rarityList: List[str]):
	caliber: str = list(caliberRequestMap.keys())[0]  # all
	# caliber: str = list(caliberRequestMap.keys())[1]  # top

	print(f'{caliber} →')
	currentJsonPath: str = f'data/{caliber}Master.json'
	with open(currentJsonPath, 'r', encoding='utf-8') as jsonFileHandler:
		master: Dict = json.load(jsonFileHandler)

	for color in 'WUBRG':
		# print(f'\n🌊 color: {color}')

		# take the first n items of a set rarity and display them
		# TODO print stats! → # GIH, GIH WR, OH WR, IWD, zScore, grade
		maxCount: int = 10
		count: int = 0
		cardFetchList: List[str] = []
		for key, value in master.items():
			if value.get("Rarity") in rarityList:
				print(f'{value.get("Name")} → {value.get("Color")}')
				if color in value.get("Color"):
					nGih: int = value['filteredStats']['all']['# GIH']
					if nGih > minGihSampleSize:
						cardFetchList.append(key)
					count += 1

					if count >= maxCount:
						break

		printCardComparison(cardFetchList, 'all', caliber)


displayTopCardsInEachColorByRarity(['C'])
