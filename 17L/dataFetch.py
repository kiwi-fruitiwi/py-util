"""
this takes some time to run!

fetch JSON data from 17L users and color filters:
	output 11 json files: the default 17L data, plus all 10 color pairs

example request uses this URL:
	https://www.17lands.com/card_ratings/data?
		expansion=LTR
		&format=PremierDraft
		&start_date=2023-06-20
		&end_date=2023-06-21
		&colors=WU
		&user_group=top
"""
import requests
import json
from constants import colorPairs


def main():
	# it's possible to leave out start and end date. defaults to entire format!
	defaultUrl: str = 'https://www.17lands.com/card_ratings/data?' \
		  'expansion=LTR' \
		  '&format=PremierDraft'

	# url for request to which we append '&colors=' and one of the 10 color pairs
	colorUrl: str = defaultUrl + '&colors='

	# iterate through colorPairs, making a request for each pair
	# then dump into 📂ltr-auto as 'allColors.json' or the colorPair name

	# first, the 'default.json' output
	allColors = requests.get(defaultUrl).json()
	with open('data/ltr-auto/default.json', 'w', encoding='utf-8') as json_file_handler:
		json_file_handler.write(json.dumps(allColors, indent=4))

	print(f'🥭 requests complete: [default', end='')


	# now we iterate through colorPairs and get a custom json for each pair
	for colorPair in colorPairs:
		coloredURL: str = f'{defaultUrl}&colors={colorPair}'
		colorPairJson = requests.get(coloredURL).json()

		# save locally to 'WU.json', 'WG.json', etc.
		with open(f'data/ltr-auto/{colorPair}.json', 'w', encoding='utf-8') \
			as json_file_handler:
			json_file_handler.write(json.dumps(colorPairJson, indent=4))
		print(f', {colorPair}', end='')
	print(f']')


main()