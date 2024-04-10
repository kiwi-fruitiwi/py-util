# download scryfall JSON data with pagination for any given set
# https://api.scryfall.com/cards/search?q=set:${setName}
from typing import Dict

import requests
import json
from constants import extraCardsForEachSet


# makes a scryfall API request and saves the file to setName.json
def getScryfallJson():
	setName: str = 'big'

	# 'the list' and 'special guests' are part of 🗡️mkm but require large
	# queries of individual cards

	# note we can append '+OR+set:MOM' to add additional sets
	baseRequestURL: str = f'https://api.scryfall.com/cards/search?q='
	requestURL: str = f'{baseRequestURL}set:{setName}'

	# used for standard bonus sheets like MAT→🦿MOM, 🍂WOT→🍁WOE
	if setName in extraCardsForEachSet:
		requestURL += f'+OR+{extraCardsForEachSet[setName]}'

	data = requests.get(requestURL).json()

	# final result json ← concatenation of all 🔑:data pages
	result = data['data']

	# pagination offers another page if 🔑:has_more is true
	while data['has_more']:
		print(f'🐳 🔑has_more!')
		nextRequestURL: str = data['next_page']
		data = requests.get(nextRequestURL).json()

		# add new pagination 🔑:data items to the results list
		result.extend(data['data'])

	print(f'{len(result)} cards found in {setName}')


	with open(f'scryfall-{setName}.json', 'w', encoding='utf-8') as json_file_handler:
		json_file_handler.write(json.dumps(result, indent=2))



getScryfallJson()