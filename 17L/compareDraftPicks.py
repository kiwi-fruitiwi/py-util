import json
import os
import time
import humanize

from fuzzywuzzy import process
from typing import List, Dict
from scryfallCardFetch import printCardText
from datetime import datetime
# import just for 🔑 names
from constants import caliberRequestMap, ANSI
from constants import colorPairs
from cardDisplay import printCardComparison, printArchetypesData

displayCardFetchList: bool = False


def getFileModifiedDescription(filePath: str) -> str:
	try:
		# get the file's status information using os.stat()
		fileStat = os.stat(filePath)

		# extract the date of last modification from the file's status info
		modifiedTimestamp = fileStat.st_mtime
		datetimeObject = datetime.fromtimestamp(modifiedTimestamp)
		timeAgo: str = humanize.naturaltime(datetimeObject)

		return timeAgo

	except FileNotFoundError:
		print(f"[ WARNING ] ⚠️ File not found.")
		return None


# returns the colorPair / colorFilter prefix from a userInput string
# 'WG: Frodo Baggins, Samwise Gamgee, Wose Pathfinder' → 'WG'
def getColorFilterPrefix(s: str) -> str:
	if len(s.split(':')) != 2:
		raise ValueError(f'color filter prefix not found in: {s}')

	colorFilter: str = s.split(':')[0].upper()
	return colorFilter


# main input loop to ask for user input → return list of card stats
# main includes
# 	the input logic: `!` and `colorPair: ` prefixes
# 	performs fuzzy matching on card names
# 	calls **printCardData** using the selected colorPair json file
# 	(or the default all colors file)
def main():
	previousUserInput: str = ''

	# load all players card stats
	caliber = list(caliberRequestMap.keys())[0]  # all players
	dataSetPath: str = f'data/{caliber}Master.json'
	print(f'\n📉 17L data update: {getFileModifiedDescription(dataSetPath)}')

	# load all players data
	with open(dataSetPath) as file:
		masterJson: Dict = json.load(file)

	# load card info from scryfall json
	with open('data/scryfall.json', encoding='utf-8-sig') as f:
		scryfallJson = json.load(f)
		'''
		card data from scryfall, including oracle text and img links
		'''

	global displayCardFetchList
	done: bool = False

	while not done:
		printFlag = False
		userInput: str = input('\nEnter cards: ')

		# special command: empty line
		# negates previous caliber if empty line is the user input
		# previous query to 'all' caliber set becomes 'top' and vice versa
		if userInput == '':
			userInput = previousUserInput

			# this is the first time we're in the input loop. restart if initial
			# input is nothing
			if userInput == '':
				continue

			# set the revised userInput to not include the top players flag if
			# it does contain it
			if userInput[0] == '~':
				userInput = userInput[1:]
				# print(f'🍋 top player flag detected in previous query. new query:\n {userInput}')
			else:
				userInput = f'~{userInput}'
				# print(f'🥭 all players detected in previous query. switching to top')

		# special command: colorPair followed by ':'
		# We can choose either prefix or suffix ':' → :wu or wu:
		# If previousUserInput is null, then continue
		# If the latter we can verify userInput[2] == ':' and len(userInput)==3
		# Assert userInput[0:2] in colorPairs before adjusting previous query
		# But need to check if the previous query also had a colorPair
		# Remove it by checking for userInput[2] == ':' and
		# 	taking previousUserInput[3:]

		# one of the problems with checking for ':' at index 2 is if colorPairs
		# include tri-colors. so maybe we can use split for ':', check len
		# then take the split(':')[0]

		# check if last character of userInput is ':' and if total length <= 5
		# <6 because the longest possible colorPair is 'WUBRG'
		if userInput[-1] == ':' and len(userInput) < 6:

			# if this is the first iteration, ignore this command
			if previousUserInput == '':
				continue

			colorFilter: str = getColorFilterPrefix(userInput)

			print(
				f'🏳️‍🌈 color filter: '
				f'{ANSI.WHITE.value}{colorFilter}{ANSI.RESET.value}')
			assert colorFilter in colorPairs

			# strip previousUserInput colorPair prefix filter
			# note that splitting by ':' checks for existence of ':'
			if len(previousUserInput.split(':')) == 2:
				previousInputSansFilter: str = previousUserInput.split(':')[1]
			else:
				previousInputSansFilter: str = previousUserInput

			# assign color filter prefix to stripped previous user input
			userInput = f'{colorFilter}:{previousInputSansFilter}'
			# print(f'[ DEBUG ] assigning userInput in filter block: {userInput}')




		# split the input string into a list using ',' as delimiter
		inputCardNames: List[str] = userInput.split(',')

		# trim leading and trailing whitespace
		strippedCardNames: List[str] = [name.strip() for name in inputCardNames]

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
		else:
			# default to caliber = all players data
			caliber = list(caliberRequestMap.keys())[0]

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
		# print(f'[ DEBUG ] previous user input saved: {previousUserInput}')


main()
