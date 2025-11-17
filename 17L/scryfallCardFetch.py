# console app to get scryfall card text with fuzzy matched name from user input
# incorporated into compareDraftPicks.py via import

import json
import re

from fuzzywuzzy import process
from typing import List
from constants import ANSI


def printCardText(cardName: str, scryfallJson):
	# iterate through scryfall data to find the matching unique card name
	# then return the text! ⚠️ note that scryfall data is not keyed by card
	# name! thus iteration
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


		# get the actual name. special case if it's an omenpaths set
		# scryfall shows 🔑name as the spm name, not 🌌ᴼᴹ¹ 🔑printed_name
		# there are three cases in two branches:
		#	normal non-omenpaths set: has 🔑name
		#     we have to account for ' // ' split cards
		#	  every card face needs to be output
		#   omenpaths set: has 🔑name for spm, 🔑printed_name for 🌌ᴼᴹ¹
		#	  take the printed_name
		#     but also need to check for ' // ' split cards ← third case


		# omenpaths cards that aren't double face: .get() falls back to 🔑name
		# if 🔑printed_name doesn't exist
		name: str = element.get('printed_name', element['name'])

		# omenpaths cards that are double face, but we need to get the name
		# of each face first!
		if ' // ' in name and 'printed_name' in element['card_faces'][0]:
			name: str = element['card_faces'][0]['printed_name']

			# seek matches, then print all faces
			if cardName in name:
				for face in element['card_faces']:
					print(f'{getCardFaceText(face, face['printed_name'], element["rarity"])}', end='')
		else:
			# for non-omenpath multi-faced cards like adventures in Wilds of Eldraine 🍁
			# iterate through all card faces and print each one
			# spaces avoids cards like SP//dr
			if cardName in name and ' // ' in name:
				for face in element['card_faces']:
					print(
						f'{getCardFaceText(face, face['name'], element["rarity"])}',
						end='')

			else: # normal or omenpaths single face cards
				if cardName == name:
					print(f'{getCardFaceText(element, name, element["rarity"])}')


def getCardFaceText(face: dict, name: str, rarity: str):
	"""
	returns card text for one face of a card
	:param name:
	:param face:
	:param rarity:
	:return:
	"""
	manaCost: str = face['mana_cost']
	typeLine: str = f'{face["type_line"]}'
	oracleText: str = face['oracle_text']

	# process oracle text to remove reminder text: everything inside parens:
	#	\( 		→ opening paren
	# 	.*?		→ any number of characters
	#	\)		→ closing paren
	parenRegex: str = r'\(.*?\)'
	oracleText = re.sub(parenRegex, '', oracleText)

	# stringBuilder: piece together the typeText output we want
	textOutput: str = ''

	textOutput += f'\n'
	textOutput += f'{ANSI.WHITE.value}{name}{ANSI.RESET.value} {manaCost}\n'
	textOutput += f'{typeLine}\n'
	textOutput += f'{ANSI.DIM_WHITE.value}{rarity.title()}{ANSI.RESET.value}\n'
	textOutput += f'{oracleText}\n'

	# only creatures, artifact creatures, and vehicles have p/t
	if 'power' in face:
		power: str = face['power']
		toughness: str = face['toughness']
		textOutput += f'{power}/{toughness}\n'

	if 'flavor_text' in face:
		flavorText: str = face['flavor_text']
		textOutput += f'{ANSI.DIM_WHITE.value}{flavorText}{ANSI.RESET.value}\n'

	return textOutput


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
	with open('data/otj-intermediate/scryfall.json', encoding='utf-8-sig') as file:
		sfData = json.load(file)

	cardNames: List = getCardNames(sfData)
	while True:
		userInput: str = input('\nEnter card: ')

		# extract the most closely matching card name from the data set:
		#   extractOne returns a tuple, e.g. ('Arwen Undómiel', 90)
		bestMatch = process.extractOne(userInput.strip(), cardNames)
		targetName: str = bestMatch[0]  # get just the 'Arwen Undómiel' part
		printCardText(targetName, sfData)