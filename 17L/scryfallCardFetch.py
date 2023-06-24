# console app to get scryfall card text with fuzzy matched name from user input

import json
from fuzzywuzzy import process
from typing import List, Dict

sfData: Dict = {}

# load card info from scryfall json
with open('data/ltr/scryfall-ltr.json', encoding='utf-8-sig') as file:
	sfData = json.load(file)

	cardNames: List = []

	# create list of card names first
	for element in sfData:
		name: str = element['name']
		cardNames.append(name)

	done: bool = False

	while not done:
		userInput: str = input('\nEnter card: ')

		# extract the most closely matching card name from the data set:
		#   extractOne returns a tuple, e.g. ('Arwen Undómiel', 90)
		bestMatch = process.extractOne(userInput.strip(), cardNames)
		targetName: str = bestMatch[0]  # get just the 'Arwen Undómiel' part


		for element in sfData:
			# for now, ignore multiple face cards like invasions and MDFCs
			# if element['card_faces']:
			#	frontFace = element['card_faces'][0]
			#	multipleCardFaces = True

			# example 🔑 json keys in each scryfall card object
			# 	"mana_cost": "{1}{G}{W}",
			# 	"cmc": 3,
			# 	"type_line": "Legendary Creature — Human Ranger",
			#	"oracle_text": "Whenever the Ring tempts you, ..."

			name: str = element['name']
			if targetName == name:
				manaCost: str = element['mana_cost']
				typeLine: str = element['type_line']
				oracleText: str = element['oracle_text']

				print(f'{name} {manaCost}')
				print(f'{typeLine}')
				print(f'{oracleText}')

				if 'power' in element:
					power: str = element['power']
					toughness: str = element['toughness']
					print(f'{power}/{toughness}')

				if 'flavor_text' in element:
					flavorText: str = element['flavor_text']
					print(f'{flavorText}')