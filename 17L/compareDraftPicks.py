import json
import os
import re
import humanize


from fuzzywuzzy import process
from typing import List, Dict, KeysView
from scryfallCardFetch import printCardText
from datetime import datetime

# import just for 🔑 names
from constants import caliberRequestMap, ANSI, colorPairs, baseRequestURL
from cardDisplay import printCardComparison, printArchetypesData

displayCardFetchList: bool = False


def getFileModifiedDescription(filePath: str) -> str or None:
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
	previousCardFetchList: List[str] = []

	# extract data start date from constants.baseRequestURL
	# regex pattern to match 'start_date=YYYY-MM-DD'
	pattern = re.compile(r"start_date=(\d{4}-\d{2}-\d{2})")
	match = pattern.search(baseRequestURL)
	dateStr: str = ''
	if match:
		dateStr = f', starting from {match.group(1)}'

	# check timestamp on default data file
	dataSetPath: str = f'data/{list(caliberRequestMap.keys())[0]}Master.json'
	print(
		f'\n📉 17L data update: {getFileModifiedDescription(dataSetPath)}'
		f'{dateStr}'
	)


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

		# 🌟 special command: empty line
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
				# print(f' top player flag detected in previous query. new query:\n {userInput}')
			else:
				userInput = f'~{userInput}'
				# print(f' all players detected in previous query. switching to top')


		# 🌟 special command: '+'
		# if the previous query were, for example:
		# 	→ survivor, firebrand, bath song, relentless
		# user input = '+ goldberry, riddermark' should append to the old query
		#	we literally append to the previousUserInput without the '+'
		#	then we process as normal
		if userInput[0] == '+':
			# ignore just the '+' character followed by an empty line
			if len(userInput) > 1:
				userInput = f'{previousUserInput}, {userInput[1:]}'
			else:
				userInput = previousUserInput

		# 🌟 special command: '-'
		# we need masterJson to be loaded to execute this one
		# remove card names from previous query, then run query again as normal
		userWishesToDeleteEntries: bool = False
		userDeletionInput: str = ''
		if userInput[0] == '-':
			# save the subtraction user input, set a flag
			userWishesToDeleteEntries = True
			userDeletionInput: str = userInput[1:]

			# take previousUserInput as the input we're going to work with
			# because we're going to remove from this later after all other
			# processing is done!
			userInput = previousUserInput


		# 🌟 special command: colorPair followed by ':'
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


		# after the userInput modifications above, now we can gather data from
		# the input

		# split the input string into a list using ',' as delimiter
		inputCardNames: List[str] = userInput.split(',')

		# trim leading and trailing whitespace
		strippedCardNames: List[str] = [name.strip() for name in inputCardNames]


		firstElement: str = strippedCardNames[0]
		# load data based on first character: '~' means top players. default:all
		if firstElement[0] == '~':
			caliber = list(caliberRequestMap.keys())[1]  # top players

			# remove special command flag but preserve first token
			firstElement = firstElement[1:].strip()
		else:
			# default to all players data instead of top
			caliber = list(caliberRequestMap.keys())[0]

		# load the data
		dataSetPath: str = f'data/{caliber}Master.json'
		with open(dataSetPath) as file:
			masterJson: Dict = json.load(file)

		# stats for current caliber
		with open(f'data/{caliber}Stats.json') as file:
			statsJson: Dict = json.load(file)


		# 🌟 special command: print card text if first char is '!'
		# we ignore all but the first token in the input string this way
		if firstElement[0] == '!':
			cardName: str = firstElement[1:].strip()  # remove '!' and spaces
			bestMatch = process.extractOne(cardName, masterJson.keys())

			# process always returns a list even if its length is 1
			printCardText(bestMatch[0], scryfallJson)

			# stop here! no need to print data if we're just checking oracleText
			continue

		# dataset we'll be loading from json. default is 'all'
		# this is not to be confused with caliber: 'top' vs 'all'
		# instead, this is 'all colors' vs 'wu', 'wg', 'ur', 'ug', etc.
		dataSetID: str = f'all'

		# 🌟 special command: colorPair with colon, e.g. 'WU: '
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
		cardFetchList: List[str] = \
			getBestCardNameMatches(masterJson.keys(), strippedCardNames)


		# handle if we detected the 🌟 subtraction special command op, '-'
		# TODO maybe don't need flag; can check non-empty string
		if userWishesToDeleteEntries:
			# get card name matches from userDeletionInput
			deletionInputCardNames: List[str] = userDeletionInput.split(',')
			strippedNames: List[str] = [name.strip() for name in deletionInputCardNames]

			cardsPendingDeletion: List[str] = \
				getBestCardNameMatches(masterJson.keys(), strippedNames)

			# remove all cards pending deletion from cardFetchList
			# 🐛 note this does not modify previousUserInput
			cardFetchList = [name for name in cardFetchList if name not in cardsPendingDeletion]


		# if there's only one card, we will show an archetype analysis!
		if len(cardFetchList) == 1:
			cardName: str = cardFetchList[0]
			printArchetypesData(cardName, masterJson, statsJson, caliber)
		else:
			# print a list of names if we're matching more than one card
			if displayCardFetchList:
				[print(name) for name in cardFetchList]

			# 🎂 display the card stats!
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


def getBestCardNameMatches(
		cardNames: KeysView[str], strippedCardNames: List[str]) -> List[str]:

	cardFetchList: List[str] = []
	for name in strippedCardNames:
		# extractOne returns a tuple like this: ('Arwen Undómiel', 90)
		# we're just interested in the name, not the closeness
		bestMatch = process.extractOne(name, cardNames)

		if bestMatch:
			bestMatchName = bestMatch[0]  # process always returns a List
			cardFetchList.append(bestMatchName)
		else:
			print(f'🍆 best match not found for {name}')
	return cardFetchList


main()
