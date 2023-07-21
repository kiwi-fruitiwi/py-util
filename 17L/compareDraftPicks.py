import json

from fuzzywuzzy import process
from typing import List, Dict
from scryfallCardFetch import printCardText

# import just for 🔑 names
from constants import caliberRequestMap
from constants import colorPairs

from cardDisplay import printCardComparison, printArchetypesData


displayCardFetchList: bool = False


# main input loop to ask for user input → return list of card stats
# main includes
# 	the input logic: `!` and `colorPair: ` prefixes
# 	performs fuzzy matching on card names
# 	calls **printCardData** using the selected colorPair json file
# 	(or the default all colors file)
def main():
	previousUserInput: str = ''

	# load card info from scryfall json
	with open('data/scryfall.json', encoding='utf-8-sig') as f:
		scryfallJson = json.load(f)
		'''
		card data from scryfall, including oracle text and img links
		'''

	global displayCardFetchList
	done: bool = False
	masterJson: Dict = {}  # load this later based on special command

	while not done:
		printFlag = False
		userInput: str = input('\nEnter cards: ')

		# special command: only '~' performs a re-query of the last query but
		# for dataSetID = 'top'

		# check userInput for just `~`, which means we want to requery with the
		# last input, but for top players
		if userInput == '~':
			userInput = previousUserInput

			# check for double '~'
			if userInput[0] != '~':
				userInput = f'~{userInput}'

		# TODO consider the opposite function: no input re-queries with 'all'
		# also avoids null input error
		if userInput == '':
			userInput = previousUserInput

			# set the revised userInput to not include the top players flag if
			# it does contain it
			if userInput[0] == '~':
				userInput = userInput[1:]

		# split the input string into a list using ',' as delimiter
		inputCardNames: List[str] = userInput.split(',')

		# trim leading and trailing whitespace
		strippedCardNames: List[str] = [name.strip() for name in inputCardNames]


		# special command: load top data set if first char is '~'
		firstElement: str = strippedCardNames[0]
		caliber = list(caliberRequestMap.keys())[0]  # all players
		dataSetPath: str = f'data/{caliber}Master.json'
		# load all players data
		with open(dataSetPath) as file:
			masterJson: Dict = json.load(file)

		# special command: print card text if first char is '!'
		# we ignore all but the first token in the input string this way
		firstElement: str = strippedCardNames[0]
		if firstElement[0] == '!':
			cardName: str = firstElement[1:].strip()  # remove '!' and spaces
			bestMatch = process.extractOne(cardName, masterJson.keys())

			# process always returns a list even if its length is 1
			printCardText(bestMatch[0], scryfallJson)

			# stop here! no need to print data if we're just checking oracleText
			continue

		if firstElement[0] == '~':
			# load top players data
			caliber = list(caliberRequestMap.keys())[1]  # top players
			dataSetPath: str = f'data/{caliber}Master.json'

			# remove special command flag but preserve first token
			firstElement = firstElement[1:].strip()
			with open(dataSetPath) as file:
				masterJson: Dict = json.load(file)

		# dataset we'll be loading from json. default is 'all'
		dataSetID: str = f'all'

		# special command: colorPair with colon, e.g. 'WU: '
		# check if first element contains ':'. use this to determine what
		# 	this will open data from the corresponding file and cache it
		# strip after in case there are multiple spaces after 'WU:'
		if ':' in firstElement:
			tokens: List[str] = firstElement.split(':')

			# there should be only two tokens: colorPair: cardName
			# and colorPair must be in [WU, WB, WR, WG, etc.]
			assert len(tokens) == 2
			assert tokens[0].upper() in colorPairs

			# save what our current data set is so it's visible in the output
			dataSetID = tokens[0].upper().strip()
			strippedCardNames[0] = tokens[1].strip()


		# set up list of card names matched to our input
		cardFetchList: List[str] = []

		for name in strippedCardNames:
			# extractOne returns a tuple like this: ('Arwen Undómiel', 90)
			# we're just interested in the name, not the closeness
			bestMatch = process.extractOne(name, masterJson.keys())

			if bestMatch:
				bestMatchName = bestMatch[0]  # process always returns a List
				cardFetchList.append(bestMatchName)
			else:
				print(f'🍆 best match not found for {name}')

		# if there's only one card, we will show an archetype analysis!
		if len(cardFetchList) == 1:
			cardName: str = cardFetchList[0]
			printArchetypesData(cardName, masterJson[cardName], caliber)
		else:
			# print a list of names if we're matching more than one card
			if displayCardFetchList:
				[print(name) for name in cardFetchList]

			printCardComparison(
				cardFetchList,
				dataSetID,
				caliber
			)

		# if there's only one card name input and it's preceded by '!'
		# → print the card's spoiler text
		# recall that printFlag is set when user input is prefixed with '!'
		if printFlag and len(cardFetchList) == 1:
			printCardText(cardFetchList[0], scryfallJson)

		# save our old userInput
		previousUserInput = userInput



main()