import Levenshtein  # makes finding the L-distance between strings much faster
import json
import statistics

from fuzzywuzzy import process
from typing import List, Dict
from scryfallCardFetch import printCardText
from constants import colorPairs, minimumSampleSize

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


MIN_SAMPLE_SIZE: int = 200


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
# main includes
# 	the input logic: `!` and `colorPair: ` prefixes
# 	performs fuzzy matching on card names
# 	calls **printCardData** using the selected colorPair json file
# 	(or the default all colors file)
def main():
	# load card info from scryfall json
	with open('data/ltr-manual/scryfall-ltr.json', encoding='utf-8-sig') as f:
		scryfallJson = json.load(f)

	nameManacostDict: Dict = generateNameManacostDict(scryfallJson)

	global compareOne
	global displayCardFetchList

	done: bool = False

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
			printFlag: bool = True
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
		dataSetUri: str = f'{dataSetRoot}default.json'
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
			# note it's either the default "all colors" json or one of the
			# colorPairs: WU WB WR WG etc.
			currentJsonStr = tokens[0].upper()

		# load specific colorPair or default 17L data from cached json
		with open(dataSetUri) as file:
			dataSet = json.load(file)

		# set up list of card names matched to our input
		cardFetchList: List[str] = []

		for value in values:
			# extractOne returns a tuple like this: ('Arwen Undómiel', 90)
			# we're just interested in the name, not the closeness
			bestMatch = process.extractOne(value, dataSet.keys())

			if bestMatch:
				bestMatchName = bestMatch[0]
				cardFetchList.append(bestMatchName)
			else:
				print(f'🍆 best match not found for {value}')

		# iterate through all color pairs and print the data there!
		if len(cardFetchList) == 1:
			for colorPair in colorPairs:
				dataSetUri = f'{dataSetRoot}{colorPair}.json'
				# load 17L data from cached json
				with open(dataSetUri) as file:
					dataSet = json.load(file)
				printCardData(cardFetchList, nameManacostDict, colorPair)

			pass
		# compareOne = True
		else:
			compareOne = False  # use newlines to reduce clutter for big tables
			# print a list of names if we're matching more than one card
			if displayCardFetchList:
				[print(name) for name in cardFetchList]
		printCardData(cardFetchList, nameManacostDict, currentJsonStr)

		# if there's only one card name input and it's preceded by '!'
		# → print the card's spoiler text
		# recall that printFlag is set when user input is prefixed with '!'
		if printFlag and len(cardFetchList) == 1:
			printCardText(cardFetchList[0], scryfallJson)


# get card data from data/master.json and display it for each cardName in
# cardNameList! The dataSet is parameterized. If the JSON is sorted by GIHWR,
# so will the results.
def printCardData(
		cardNameList: List[str], nameManacostDict, dataSetStr: str):
	global compareOne
	global displayIwdGrade, displayGihOhDiff, displayOhZscore, \
		displayRarityAndMv

	# open master.json to query for data
	# sample master.json
	# "Birthday Escape": {
	# 	"Name": "Birthday Escape",
	# 	"ALSA": 4.787610685652746,
	# 	"ATA": 6.028844661098519,
	# 	"URL": "https://cards.scryfall.io/border_crop/front/4/2/42db2313-b13d-4292-bef2-bf86f989d32f.jpg?1686169032",
	# 	"Color": "U",
	# 	"Rarity": "C",
	# 	"filteredStats": {
	# 		"default": {
	# 			"GIH WR": 0.5960239727329169,
	# 			"OH WR": 0.5751692517104273,
	# 			"# GIH": 78923,
	# 			"# OH": 27917,
	# 			"IWD": 0.06738294709189119
	# 		},
	# 		"WU": {
	# 			"GIH WR": 0.5773472122024116,
	# 			"OH WR": 0.54628269174258,
	# 			"# GIH": 9703,
	# 			"# OH": 3403,
	# 			"IWD": 0.07841650219385726
	# 		},
	currentJsonPath: str = f'data/master.json'
	with open(currentJsonPath, 'r', encoding='utf-8') as jsonFileHandler:
		masterData: Dict = json.load(jsonFileHandler)

	# extra newline if we're comparing multiple cards
	if not compareOne:
		print('')

	def sortingKey(item, stat: str):
		data: Dict = item[1]  # note that item[0] is the 🔑 cardName
		value = data['filteredStats'][dataSetStr][stat]
		if value is None:
			return float('-inf')
		return value

	# note that to obtain stats for a colorPair, we query
	# data['filteredStats'][dataSet], where dataSet ⊂ {default, WU, UG, WR...}
	# sample dictionary:
	#	"WU": {
    # 		"GIH WR": 0.5773472122024116,
    # 		"OH WR": 0.54628269174258,
    # 		"# GIH": 9703,
    # 		"# OH": 3403,
    # 		"IWD": 0.07841650219385726
	#	},

	# TODO this requires the cardName
	# colorPairStats: Dict = masterData['filteredStats'][dataSet]

	# sort by GIH WR manually in case it's not already sorted that way in csv
	# TODO figure out what we're sorting by: do we need dataSet: GIH WR?
	sortedData = dict(
		sorted(
			masterData.items(),
			key=lambda item: sortingKey(item, 'GIH WR'),
			reverse=True)
	)

	# open the statistics data file to query for μ, σ
	currentJsonPath: str = f'data/statistics.json'
	with open(currentJsonPath, 'r', encoding='utf-8') as statsFileHandler:
		cardStatistics: Dict = json.load(statsFileHandler)


	# grab the mean and standard deviation from statistics.json:
	#     "WU": {
	#         "GIH WR": {
	#             "mean": 0.5491077666469387,
	#             "stdDev": 0.040215101426471105
	#         },
	#         "OH WR": {
	#             "mean": 0.5209195619740031,
	#             "stdDev": 0.042789373519670264
	#         },
	#         "IWD": {
	#             "mean": 0.061158040767395096,
	#             "stdDev": 0.04112565649327313
	#         }
	#     },
	gihwrMean: float = cardStatistics[dataSetStr]['GIH WR']['mean']
	gihwrStdDev: float = cardStatistics[dataSetStr]['GIH WR']['stdDev']
	ohwrMean: float = cardStatistics[dataSetStr]['OH WR']['mean']
	ohwrStdDev: float = cardStatistics[dataSetStr]['OH WR']['stdDev']

	displayHeader(dataSetStr, gihwrMean, gihwrStdDev)

	# now that we have the GIH WR σ and μ, display data:
	for cardName, cardData in sortedData.items():

		# some cards don't have data: check if it's actually in our GIHWR dict
		# TODO check if # GIH reaches a threshold for it to be included!
		# TODO are these parens redundant?
		# if (cardData['# GIH'] > minimumSampleSize) and (cardName in cardNameList):
		if cardName in cardNameList:

			# this contains the 5 pieces of data specific to this colorPair
			cardStats: Dict = cardData['filteredStats'][dataSetStr]
			gihwr: float = cardStats['GIH WR']
			nGih: int = cardStats['# GIH']  # number of times seen in hand
			ohwr: float = cardStats['OH WR']
			nOh: float = cardStats['# OH']
			iwd: float = cardStats['IWD']

			# note '🔑 color' is not in filteredStats
			color: str = cardData['Color']
			rarity: str = cardData['Rarity']

			# initialize strings for grades, e.g. A-, C+, B, S
			gihwrGrade: str = ' '  # empty space for alignment
			ohwrGrade: str = ' '
			iwdGrade: str = ' '

			# only process data if sample size is significant
			if nGih > minimumSampleSize:
				# calculate how many stdDevs away from the mean?
				# zscore = (x-μ) / σ
				gihwrZScore: float = (gihwr - gihwrMean) / gihwrStdDev

				# iterate reversed gradeBounds list: ('A+', 2.17) ('B', 0.83)
				# if zScore is greater than current iterated value:
				# 	replace gradeStr with key: 'A+', 'B', etc.

				# TODO encapsulate grade-finding based on parameter: stat
				# e.g. GIH WR, OH WR, IWD
				for gradePair in gradeBounds[::-1]:
					if gihwrZScore >= gradePair[1]:
						gihwrGrade = gradePair[0]

				ohwrZScore: float = (ohwr - ohwrMean) / ohwrStdDev

				alsa: float = float(cardData["ALSA"])

				ohwrStr: str = f'{ohwr * 100:4.1f}%' if ohwr else f'    -'

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
				if displayRarityAndMv:
					# 8 spaces needed for rarity and mana cost, +1 space
					# mv must be 6 because 3WUBRG costs
					rarityMvStr = f'{rarity} {manacost:6} '

				iwdStr: str = f'{iwd * 100:.1f}pp'

				# each row
				print(
					f'{gihwrGrade:2} '
					f'{alsa:4.1f} '
					f'{gihwr * 100:4.1f}% '
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
					f'                                 '
					# f'← {rarity} {manacost:5} {cardName}'
					f'← {cardName}'
				)


# displays the header for the data set, including set name, mean, and stdDev
def displayHeader(dataSet: str, μ: float, σ: float):
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
		f'{dataSet} μ:{μ:.3f}, σ:{σ:.3f}'
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