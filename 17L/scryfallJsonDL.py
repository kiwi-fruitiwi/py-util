# download scryfall JSON data with pagination for any given set
# https://api.scryfall.com/cards/search?q=set:${setName}
from typing import Dict

import requests
import json
from constants import extraCardsForEachSet, setName


# makes a scryfall API request and saves the file to setName.json
# setName is set in constants.py → setName
# constants.py also include what extra cards are in the set
def getScryfallJson():
	# 'the list' and 'special guests' are part of 🗡️mkm but require large
	# queries of individual cards

	# scryfall rejects the default python userAgent
	headers = {
		"User-Agent": "scryfallJsonDL-script/0.1",
		"Accept": "application/json;q=0.9,*/*;q=0.8",
	}


	# note we can append '+OR+set:MOM' to add additional sets
	baseRequestURL: str = f'https://api.scryfall.com/cards/search?q='
	requestURL: str = f'{baseRequestURL}set:{setName}'

	# used for standard bonus sheets like MAT→🦿MOM, 🍂WOT→🍁WOE
	if setName in extraCardsForEachSet:
		requestURL += f'+OR+{extraCardsForEachSet[setName]}'

	data = requests.get(requestURL, headers=headers).json()
	print(f'request URL → {requestURL}')

	if "data" not in data:
		raise RuntimeError(f"Scryfall did not return card data: {data}")

	# final result json ← concatenation of all 🔑:data pages
	result = data['data']

	# pagination offers another page if 🔑:has_more is true
	while data['has_more']:
		print(f'🐳 🔑has_more!')
		nextRequestURL: str = data['next_page']
		data = requests.get(nextRequestURL, headers=headers).json()

		# add new pagination 🔑:data items to the results list
		result.extend(data['data'])

	print(f'{len(result)} cards found in {setName}')


	# with open(f'scryfall-{setName}.json', 'w', encoding='utf-8') as json_file_handler:
	with open(f'scryfall.json', 'w', encoding='utf-8') as json_file_handler:
		json_file_handler.write(json.dumps(result, indent=2))


getScryfallJson()