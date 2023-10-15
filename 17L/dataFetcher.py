# 🪶 fetch JSON data from 17L users and color filters:
# 	output 11 json files: the default 17L data, plus all 10 color pairs
#
# this takes some time to run!
#
# example request uses this URL:
# 	https://www.17lands.com/card_ratings/data?
# 		expansion=LTR
# 		&format=PremierDraft
# 		&start_date=2023-06-20
# 		&end_date=2023-06-21
# 		&colors=WU
# 		&user_group=top


import json
import requests
from typing import Dict
from constants import caliberRequestMap, colorPairs


# get requested json data from 17lands.com for all data sets
def main():
	getRawRequestsFrom17L()

	# enable this when we don't restrict startDate so ALSAs are more accurate
	# getRecentAlsaMaps()


def getRecentAlsaMaps():
	for dataSetName, dataSetURL in caliberRequestMap.items():
		dataSetURL += f'&start_date=2023-10-01'
		print(f'🫐 processing {dataSetName} → {dataSetURL}')

		# query 17L for data for 'all' users, usually within last two weeks
		recentAllData = requests.get(dataSetURL).json()

		# create new dictionary keyed by cardName, value: float = ALSA
		# the request returns a list of dictionaries
		'''
		[
			{
				"seen_count": 10999,
				"avg_seen": 1.6191471951995635,
				"pick_count": 6771,
				"avg_pick": 1.55457096440703,
				"game_count": 35281,
				"pool_count": 40937,
				"play_rate": 0.8618364804455627,
				"win_rate": 0.5512598849238968,
				"opening_hand_game_count": 5795,
				"opening_hand_win_rate": 0.5703192407247627,
				"drawn_game_count": 8928,
				"drawn_win_rate": 0.5877016129032258,
				"ever_drawn_game_count": 14723,
				"ever_drawn_win_rate": 0.5808598791007268,
				"never_drawn_game_count": 20597,
				"never_drawn_win_rate": 0.5294945865902801,
				"drawn_improvement_win_rate": 0.051365292510446636,
				"name": "Archon of the Wild Rose",
				"mtga_id": 86683,
				"color": "W",
				"rarity": "rare",
				"url": "https://cards.scryfall.io/large/front/0/0/00174be7-0dc8-43b9-81b6-f25a8c3fb4eb.jpg?1692936281",
				"url_back": "",
				"types": [
					"Creature - Archon"
				]
			},
		'''
		result: Dict = {}
		for card in recentAllData:
			alsa: float = card['avg_seen']
			name: str = card['name']
			if '//' in card['name']:
				name = card['name'].split(' // ')[0]

			result[name] = alsa

		# export json to allRecentAlsa.json and topRecentAlsa.json
		with (open(f'data/{dataSetName}RecentAlsa.json', 'w', encoding='utf-8')
					  as json_file_handler):
			json_file_handler.write(json.dumps(result, indent=4))


def getRawRequestsFrom17L():
	for dataSetName, dataSetURL in caliberRequestMap.items():
		print(f'🫐 processing {dataSetName} → {dataSetURL}')

		# iterate through colorPairs, making a request for each pair
		# then dump into 📂requests as 'all.json' or the colorPair name

		# first, the 'all.json' output
		allColors = requests.get(dataSetURL).json()
		with open(
				f'data/requests/{dataSetName}/all.json',
				'w',
				encoding='utf-8') as json_file_handler:
			json_file_handler.write(json.dumps(allColors, indent=4))

		print(f'🍓 requests complete: [all', end='')

		# now we iterate through colorPairs and get a custom json for each pair
		for colorPair in colorPairs:
			coloredURL: str = f'{dataSetURL}&colors={colorPair}'
			colorPairJson = requests.get(coloredURL).json()

			# save locally to 'WU.json', 'WG.json', etc.
			with open(
					f'data/requests/{dataSetName}/{colorPair}.json',
					'w', encoding='utf-8') as json_file_handler:
				json_file_handler.write(json.dumps(colorPairJson, indent=4))
			print(f', {colorPair}', end='')
		print(f']')


main()
