import Levenshtein  # makes finding the L-distance between strings much faster
import json
import statistics

from fuzzywuzzy import process
from typing import List, Dict
from scryfallCardFetch import printCardText
from constants import colorPairs

# defines lower bound zScore values for letter grades like A-, D+, B, etc.
# each letter grade is one standard deviation, with C centered around the mean μ
# a list of tuples containing lower bounds for grades, e.g. S:2.5, A:1.83
# invariant: this is sorted by zScore value
gradeBounds: List[tuple] = [
	('S+', 3.0),
	('S', 2.5),
	('A+', 2.17),
	('A', 1.83),
	('A-', 1.5),
	('B+', 1.17),
	('B', 0.83),
	('B-', 0.5),
	('C+', 0.17),
	('C', 0),
	('C-', -0.17),
	('D+', -0.83),
	('D', -1.17),
	('D-', -1.5),
	('F', -10)
]


# if we're only comparing one card, skip newlines so subsequent queries
# are easier to visually compare
compareOne: bool = False
displayIwdGrade: bool = False
displayCardFetchList: bool = False
displayGihOhDiff: bool = True  # difference in zScore between GIH and OH WRs
displayOhZscore: bool = True
displayRarityAndMv: bool = False

dataSetRoot: str = 'data/ltr-CDP/'


# main input loop to ask for user input → return list of card stats
def main():
	# load card info from scryfall json
	with open('data/ltr-manual/scryfall-ltr.json', encoding='utf-8-sig') as f:
		scryfallJson = json.load(f)

	nameManacostDict: Dict = generateNameManacostDict(scryfallJson)

	global compareOne
	global displayCardFetchList

	done: bool = False
	printFlag: bool = False

	while not done:
		printFlag = False
		if not compareOne:
			print('')
		userInput: str = input('Enter cards: ')

		# split the input string into a list using ',' as delimiter
		names: List[str] = userInput.split(',')

		# trim leading and trailing whitespace
		values: List[str] = [name.strip() for name in names]

		# special command: print card text if first char is '!'
		# this is done only if there's one card name in the input
		firstElement: str = values[0]
		if firstElement[0] == '!':
			printFlag = True
			updatedFirstElement = firstElement[1:]  # remove the '!'
			values[0] = updatedFirstElement  # clobber to update value

		# special command: colorPair with colon, e.g. 'WU: '
		# 	this will open data from the corresponding file and save to json17L
		#    how do we access 17LdataFetch colorPair?
		#    load the color pair json that corresponds to it
		# strip after in case there are multiple spaces after 'WU:'

		firstElement: str = values[0]  # updated, after '!' is stripped
		# check if first element contains ':' if so, split(':')
		# use this to determine what json file we'll be loading
		dataSetUri: str = f'{dataSetRoot}all.json'
		currentJsonStr: str = f'default'

		if ':' in firstElement:
			tokens: List[str] = firstElement.split(':')

			# there should be only two tokens: colorPair: cardName
			# and colorPair must be in [WU, WB, WR, WG, etc.]
			assert len(tokens) == 2
			assert tokens[0].upper() in colorPairs

			# set our dataset to what we want!
			dataSetUri = f'{dataSetRoot}{tokens[0].upper()}.json'

			# save what our current data set is so it's visible with the data
			currentJsonStr = tokens[0]

		# load 17L data from cached json
		with open(dataSetUri) as file:
			json17L = json.load(file)

		# set up list of card names matched to our input
		cardFetchList: List[str] = []

		for value in values:
			# extractOne returns a tuple like this: ('Arwen Undómiel', 90)
			# we're just interested in the name, not the closeness
			bestMatch = process.extractOne(value, json17L.keys())

			if bestMatch:
				bestMatchName = bestMatch[0]
				cardFetchList.append(bestMatchName)
			else:
				print(f'🍆 best match not found for {value}')

		# use cardFetchList to grab JSON data from data variable
		if len(cardFetchList) == 1:
			pass
		# compareOne = True
		else:
			compareOne = False  # use newlines to reduce clutter for big tables
			# print a list of names if we're matching more than one card
			if displayCardFetchList:
				[print(name) for name in cardFetchList]
		printCardData(cardFetchList, json17L, nameManacostDict, currentJsonStr)

		# if there's only one card name input and it's preceded by '!'
		# print the card's spoiler text
		if printFlag and len(cardFetchList) == 1:
			printCardText(cardFetchList[0], scryfallJson)


# get card data from data/ratings.json and display it for each cardName in
# cardNameList! If the JSON is sorted by GIHWR, so will the results.
def printCardData(
		cardNameList: List[str], json17L, nameManacostDict, dataSet: str):
	global compareOne
	global displayIwdGrade, displayGihOhDiff, displayOhZscore, \
		displayRarityAndMv

	# create GIH WR, OH WR, IWD arrays
	gihwrList: List[float] = []
	ohwrList: List[float] = []
	iwdList: List[float] = []

	# (🔑 CardName, GIH WR) dictionary and OHWR, IWD counterparts
	nameGihwrDict: Dict[str, float] = {}
	nameOhwrDict: Dict[str, float] = {}
	nameIwdDict: Dict[str, float] = {}

	# iterate through JSON data to determine σ and μ for data set first:
	# 	both GIH WR and OH WR
	#   code below was originally written to process json converted from
	#   17L's csv export. after moving to requests, we dealt completely in
	#   floats instead of "67.0%" or "16.2pp"
	for cardName in json17L.keys():
		# some cards don't have enough data and their GIH WR is empty: ''. so
		# we can simply ignore these in the data set, e.g.
		#   invasion of arcavios
		#   jin-gitaxias, core augur
		# we use None and test for that later if data is not present

		gihwr: float = json17L[cardName]["GIH WR"]
		n_gih: int = json17L[cardName]["# GIH"]

		# IWD only exists when there's a GIHWR, so we calculate these together
		# note format is "16.8pp"
		iwd: float = json17L[cardName]["IWD"]
		iwdStr: str = f'{iwd * 100:.1f}pp'

		if n_gih < 200:
			nameGihwrDict[cardName] = None  # test for None later when printing
			nameIwdDict[cardName] = None
		else:
			gihwrList.append(gihwr)
			iwdList.append(iwd)
			nameGihwrDict[cardName] = gihwr
			nameIwdDict[cardName] = iwd

		# repeat for OH WR
		ohwr: float = json17L[cardName]["OH WR"]
		n_oh: int = json17L[cardName]["# OH"]
		if n_oh < 200:
			nameOhwrDict[cardName] = None
		else:
			ohwrList.append(ohwr)
			nameOhwrDict[cardName] = ohwr

	# [print(f'{e} → {nameIwdDict[e]}') for e in nameIwdDict]
	filteredGIHWRs = [x for x in nameGihwrDict.values() if x is not None]
	filteredOHWRs = [x for x in nameOhwrDict.values() if x is not None]
	filteredIWDs = [x for x in nameIwdDict.values() if x is not None]

	μ_gihwr: float = statistics.mean(filteredGIHWRs)
	σ_gihwr: float = statistics.stdev(filteredGIHWRs)
	μ_ohwr: float = statistics.mean(filteredOHWRs)
	σ_ohwr: float = statistics.stdev(filteredOHWRs)
	μ_iwd: float = statistics.mean(filteredIWDs)
	σ_iwd: float = statistics.stdev(filteredIWDs)

	# find μ and σ of ohwr as well
	# sort by ohwr
	# ohwrJson = dict(sorted(
	# 	json17L.items(), key=lambda item: item[1]["OH WR"], reverse=True))

	# extra newline if we're comparing multiple cards
	if not compareOne:
		print('')

	# print(f'  iwd μ:{μ_iwd:.3f}, σ:{σ_iwd:.3f}')
	# print(f' ohwr μ:{μ_ohwr:.3f}, σ:{σ_ohwr:.3f}')
	# print(f'gihwr μ:{μ_gihwr:.3f}, σ:{σ_gihwr:.3f}')
	# print(f'')

	def sortingKey(item):
		gih_wr = item[1]["GIH WR"]
		if gih_wr is None:
			return float('-inf')
		return gih_wr

	# sort by GIH WR manually in case it's not already sorted that way in csv
	gihwrJson = dict(sorted(json17L.items(), key=sortingKey, reverse=True))

	# [ HEADER ]
	# add 3 spaces for iwd grade, e.g. A+, C-
	iwdGradeHeaderStr: str = '   ' if displayIwdGrade else ''

	# 5 characters for zScore diff
	ogDifHeader: str = ' og Δ' if displayGihOhDiff else ''

	# 8 char width and a whitespace
	rarityMvHeader: str = '         ' if displayRarityAndMv else ''

	print(  # metric and how many characters each metric takes, plus spacing
		f'   '  # grade is 2 + 1 space
		f'alsa '  # ALSA 4 chars + 1 whitespace
		f'  gih '  # GIHWR: 6
		f'    z '  # gihwr zscore 5 + 1
		# f' oh-z ' 	# ohwr zscore 5 + 1
		# f'   oh '		# OHWR: 6
		f'{ogDifHeader}'
		f'    iwd '
		f'{iwdGradeHeaderStr}'
		f'{rarityMvHeader}'
		f'  '  # leading spaces for '← '
		f'{dataSet} μ:{μ_gihwr:.3f}, σ:{σ_gihwr:.3f}'
	)
	# now that we have the GIH WR σ and μ, display data:
	# note the JSON will be sorted however it was when the csv was requested
	# by default it will be by collector ID: alphabetical in wubrg order
	for cardName in gihwrJson.keys():
		# some cards don't have data: check if it's actually in our GIHWR dict
		if (cardName in nameGihwrDict) and (cardName in cardNameList):
			cardData = json17L[cardName]  # card data json object
			gihwr: float = nameGihwrDict[cardName]  # GIH WR
			ohwr: float = nameOhwrDict[cardName]  # OH WR
			iwd: float = nameIwdDict[cardName]  # IWD
			color: str = cardData["Color"]
			rarity: str = cardData["Rarity"]
			gihwrGrade: str = ' '  # empty space for alignment
			ohwrGrade: str = ' '
			iwdGrade: str = ' '

			# pretty sure ohwr has to exist if gihwr does. false, not Glamdring
			if gihwr:  # x is set to None if no GIH WR was available
				# calculate how many stdDevs away from the mean?
				gihwrZScore: float = (gihwr - μ_gihwr) / σ_gihwr

				# iterate reversed gradeBounds list: ('A+', 2.17) ('B', 0.83)
				# if zScore is greater than current iterated value:
				# 	replace gradeStr with key: 'A+', 'B', etc.
				for gradePair in gradeBounds[::-1]:
					if gihwrZScore >= gradePair[1]:
						gihwrGrade = gradePair[0]

				# repeat for ohwr
				ohwrZScore = None
				if ohwr:
					ohwrZScore: float = (ohwr - μ_ohwr) / σ_ohwr
					for gradePair in gradeBounds[::-1]:
						if ohwrZScore >= gradePair[1]:
							ohwrGrade = gradePair[0]

				iwdZScore = None
				if iwd:
					iwdZScore: float = (iwd - μ_iwd) / σ_iwd
					for gradePair in gradeBounds[::-1]:
						if iwdZScore >= gradePair[1]:
							iwdGrade = gradePair[0]

				iwdList: str = cardData["IWD"]
				alsa: float = float(cardData["ALSA"])

				# if GIH WR exists, OH WR should too, so no extra check needed
				ohwrStr: str = cardData["OH WR"]

				if ohwrStr != '':
					# ohwrList: float = float(cardData["OH WR"].replace('%', 'e-2'))
					ohwrStr: str = f'{ohwr * 100:4.1f}%'
				else:
					ohwrStr: str = f'    -'

				# display difference in zscore between GIHWR and OHWR
				ogDifStr: str = ''
				if displayGihOhDiff:
					if ohwrZScore:
						ogDif: float = ohwrZScore - gihwrZScore
						ogDifStr = f'{ogDif:5.2f}'
					else:
						ogDifStr = '    -'

				# opening hand win rate z score display
				ohwrZscoreStr: str = ''
				if displayOhZscore:
					if ohwrZScore:
						ohwrZscoreStr = f'{ohwrZScore:5.2f}'

				# grab the mana cost from our collapsed scryfall dictionary:
				# format is [cardName, mana cost] where latter is formatted
				# 1UUU instead of {1}{U}{U}{U}
				manacost: str = nameManacostDict[cardName]

				iwdGradeStr: str = ''
				if displayIwdGrade:
					iwdGradeStr = f'{iwdGrade:2} '

				rarityMvStr: str = ''
				if rarityMvHeader:
					# 8 spaces needed for rarity and mana cost, +1 space
					# mv must be 6 because 3WUBRG costs
					rarityMvStr = f'{rarity} {manacost:6} '

				iwdStr: str = f'{nameIwdDict[cardName] * 100:.1f}pp'

				# each row
				print(
					f'{gihwrGrade:2} '
					f'{alsa:4.1f} '
					f'{nameGihwrDict[cardName] * 100:4.1f}% '
					f'{gihwrZScore:5.2f} '
					# f'{ohwrZscoreStr} '
					# f'{ohwrStr} '
					f'{ogDifStr} '
					f'{iwdStr:>6} '
					f'{iwdGradeStr}'
					f'← '
					f'{rarityMvStr}'
					f'{cardName}')
			else:
				manacost: str = nameManacostDict[cardName]
				print(
					# f'← {rarity} {manacost:5} {cardName}'
					f'NA ← {cardName}'
				)


# generates a dictionary mapping card names to their mana costs in format '2UUU'
def generateNameManacostDict(sfJson):
	# iterate through scryfallData. for each object:
	#   strip {} from castingCost in format "{4}{G}{W}"
	#   execute results[name] = strippedCastingCost
	# return results
	results: Dict[str, str] = {}
	for card in sfJson:
		# strip {}, converting {2}{W}{R} to 2WR
		manaCost: str = card['mana_cost'].replace("{", "").replace("}", "")
		name: str = card['name']
		results[name] = manaCost

	return results


main()