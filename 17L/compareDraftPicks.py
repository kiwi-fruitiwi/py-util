import Levenshtein  # makes finding the L-distance between strings much faster
from fuzzywuzzy import process
from typing import List, Dict
import json
import statistics


# defines lower bound zScore values for letter grades like A-, D+, B, etc.
# each letter grade is one standard deviation, with C centered around the mean μ
# a list of tuples containing lower bounds for grades, e.g. S:2.5, A:1.83
# invariant: this is sorted by zScore value

# noinspection DuplicatedCode
gradeBounds: List[tuple] = [
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


# main input loop to ask for user input → return list of card stats
def main(data):
	done: bool = False
	while not done:
		userInput: str = input('\nEnter cards: ')

		# split the input string into a list using ',' as delimiter
		names = userInput.split(',')

		# trim leading and trailing whitespace
		values = [name.strip() for name in names]

		# set up list of card names matched to our input
		cardFetchList: List[str] = []

		for value in values:
			# extractOne returns a tuple like this: ('Arwen Undómiel', 90)
			# we're just interested in the name, not the closeness
			bestMatch = process.extractOne(value, data.keys())

			if bestMatch:
				bestMatchName = bestMatch[0]
				cardFetchList.append(bestMatchName)
			else:
				print(f'🍆 best match not found for {value}')

		# use cardFetchList to grab JSON data from data variable
		[print(name) for name in cardFetchList]
		printCardData(cardFetchList, data)


# get card data from data/ratings.json
# noinspection DuplicatedCode
def printCardData(cardNameList: List[str], jsonData):
	# load JSON converted from 17L csv export, where each entry looks like this:
	# 	"Sunfall": {
	#		"Name": "Sunfall",
	#		"Color": "W",
	#		"Rarity": "R",
	#		"# Picked": "9950",
	#		"ATA": "1.35",
	#		"# OH": "9537",
	#		"OH WR": "65.2%",
	#		"# GIH": "23564",
	#		"GIH WR": "67.0%",
	#		"IWD": "14.0pp"
	#	},

	# first create GIH WR array
	gameInHandWinRates: List[float] = []

	# CardName, GIH WR dictionary
	cardWinRates: Dict[str, float] = {}
	# iterate through JSON data to determine σ and μ for data set first

	for cardName in jsonData.keys():
		# the data is actually in string format: e.g. "GIH WR": "67.0%",
		# so we need to do the following to convert to decimal:
		#   verify right-most char is '%', then cast to float with 'e-2'

		# some cards don't have enough data and their GIH WR is empty: ''. so
		# we can simply ignore these in the data set, e.g.
		#   invasion of arcavios
		#   jin-gitaxias, core augur
		# we use None and test for that later if data is not present
		winRateString: str = jsonData[cardName]["GIH WR"]
		if winRateString != '':
			assert winRateString[-1] == '%'
			wr = float(winRateString.replace('%', 'e-2'))
			gameInHandWinRates.append(wr)
			cardWinRates[cardName] = wr
		else:
			cardWinRates[cardName] = None # test for None later when printing

	filteredWRs = [x for x in cardWinRates.values() if x is not None]

	μ: float = statistics.mean(filteredWRs)
	σ: float = statistics.stdev(filteredWRs)
	print(f'\nGIH WR μ → {μ}')
	print(f'GIH WR σ → {σ}\n')

	# now that we have the GIH WR σ and μ, display data:
	# note the JSON will be sorted however it was when the csv was requested
	# by default it will be by collector ID: alphabetical in wubrg order
	for cardName in jsonData.keys():
		# some cards don't have data: check if it's actually in our GIHWR dict
		if (cardName in cardWinRates) and (cardName in cardNameList):
			x: float = cardWinRates[cardName]  # GIH WR
			color: str = jsonData[cardName]["Color"]
			rarity: str = jsonData[cardName]["Rarity"]
			gradeStr = ' '  # empty space for alignment

			if x:  # x is set to None if no GIH WR was available
				# calculate how many stdDevs away from the mean?
				zScore: float = (x - μ) / σ

				# iterate reversed gradeBounds list: ('A+', 2.17) ('B', 0.83)
				# if zScore is greater than current iterated value:
				# 	replace gradeStr with key: 'A+', 'B', etc.
				for gradePair in gradeBounds[::-1]:
					if zScore >= gradePair[1]:
						gradeStr = gradePair[0]

				# header
				print(f'')
				print(
					f'{gradeStr:2} {zScore:7.3f} {cardWinRates[cardName]: 6.3f}'
					f' ← {rarity} [{color}] {cardName}')
			else:
				print(
					f'insufficient data: {rarity} [{color}] {cardName}')


# load json from our 17L csv to json converter
with open('data/ratings.json') as file:
	data17Ljson = json.load(file)

main(data17Ljson)