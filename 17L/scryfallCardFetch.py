# console app to get scryfall card text with fuzzy matched name from user input
# incorporated into compareDraftPicks.py via import

import json
from fuzzywuzzy import process
from typing import List, Dict


def printCardText(cardName: str, scryfallJson):
	# iterate through scryfall data to find the matching unique card name
	# then print out the text!
	for element in scryfallJson:
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
		if cardName == name:
			manaCost: str = element['mana_cost']
			typeLine: str = element['type_line']
			oracleText: str = element['oracle_text']

			print(f'')
			print(f'{name} {manaCost}')
			print(f'{typeLine}')
			print(f'{oracleText}')

			# only creatures, artifact creatures, and vehicles have p/t
			if 'power' in element:
				power: str = element['power']
				toughness: str = element['toughness']
				print(f'{power}/{toughness}')

			if 'flavor_text' in element:
				flavorText: str = element['flavor_text']
				print(f'{flavorText}')


def getCardNames(scryfallJson):
	# create list of card names first from scryfall json
	names: List[str] = []

	for element in scryfallJson:
		name: str = element['name']
		collectorNumber: int = int(element['collector_number'])

		# basic lands start at 262 and continue through 281
		if collectorNumber <= 281:
			names.append(name)
		else:
			pass
			# print(f'🍆 {name} not added')

	return names


def main():
	# load card info from scryfall json
	with open('data/scryfall.json', encoding='utf-8-sig') as file:
		sfData = json.load(file)

	cardNames: List = getCardNames(sfData)
	while True:
		userInput: str = input('\nEnter card: ')

		# extract the most closely matching card name from the data set:
		#   extractOne returns a tuple, e.g. ('Arwen Undómiel', 90)
		bestMatch = process.extractOne(userInput.strip(), cardNames)
		targetName: str = bestMatch[0]  # get just the 'Arwen Undómiel' part
		printCardText(targetName, sfData)