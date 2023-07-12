# fetch JSON data from 17L users and color filters:
# 	output 11 json files: the default 17L data, plus all 10 color pairs
#
# this takes some time to run!
#
#
# example request uses this URL:
# 	https://www.17lands.com/card_ratings/data?
# 		expansion=LTR
# 		&format=PremierDraft
# 		&start_date=2023-06-20
# 		&end_date=2023-06-21
# 		&colors=WU
# 		&user_group=top

import requests
import json
from constants import colorPairs
# from createMasterJson import createMasterJson, createStatsJson


def main():
	# it's possible to leave out start and end date. defaults to entire format!
	allColorsUrl: str = 'https://www.17lands.com/card_ratings/data?' \
		  'expansion=LTR' \
		  '&format=PremierDraft'

	# iterate through colorPairs, making a request for each pair
	# then dump into 📂ltr-requests as 'all.json' or the colorPair name

	# first, the 'all.json' output
	allColors = requests.get(allColorsUrl).json()
	with open('data/ltr-requests/all.json', 'w', encoding='utf-8') as json_file_handler:
		json_file_handler.write(json.dumps(allColors, indent=4))

	print(f'🍓 requests complete: [all', end='')


	# now we iterate through colorPairs and get a custom json for each pair
	for colorPair in colorPairs:
		coloredURL: str = f'{allColorsUrl}&colors={colorPair}'
		colorPairJson = requests.get(coloredURL).json()

		# save locally to 'WU.json', 'WG.json', etc.
		with open(f'data/ltr-requests/{colorPair}.json', 'w', encoding='utf-8') \
			as json_file_handler:
			json_file_handler.write(json.dumps(colorPairJson, indent=4))
		print(f', {colorPair}', end='')
	print(f']')


main()