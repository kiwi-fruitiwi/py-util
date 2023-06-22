# from: askpython.com/python/examples/convert-csv-to-json
# purpose: convert 17L csv data into JSON format for 🚂17L-grades
# last ratings update: 2023.06.11: top, all colors

import csv
import json
import statistics
from fuzzywuzzy import process
from typing import List, Dict


# noinspection DuplicatedCode
# TODO what type is data? json?
def getCardNamesFromUserInput(userInput: str, data: Dict[str, str]) \
		-> List[str]:
	# split the input string into a list using ',' as delimiter
	names = userInput.split(',')

	# trim leading and trailing whitespace
	values = [name.strip() for name in names]

	# set up list of card names matched to our input
	cardFetchList: List[str] = []

	for value in values:
		# extractBests returns a list of tuples
		#   → [print(e) for e in bestMatches] results in the following:
		#       ('Aragorn, the Uniter', 90)
		#       ('Gimli, Counter of Kills', 75)
		#       ('Legolas, Counter of Kills', 75)
		#       ('Mordor Muster', 66)
		#       ('Bitter Downfall', 60)
		bestMatches = process.extractBests(value, data.keys())
		bestMatchTuple = bestMatches[0]

		# we want the name part of the best match. we could use extractOne :P
		bestMatchName = bestMatchTuple[0]
		cardFetchList.append(bestMatchName)

	return cardFetchList


def csvToJSON(csvPath, jsonPath):
	"""
	take 17L csv card ratings in csv and convert them to JSON
	:param csvPath:
	:param jsonPath:
	"""
	# create a dictionary of card info
	cards = {}


	# open a csv file handler
	#
	# note: using utf-8-sig to read a file will treat the BOM as metadata that
	# explains how to interpret the file, instead of as part of the file
	# contents.
	with open(csvPath, encoding='utf-8-sig') as csv_file_handler:
		csv_reader = csv.DictReader(csv_file_handler)

		# convert each row into a dictionary; add converted data to cards dict
		for row in csv_reader:
			# primary key is the name of the card
			cardName = row['Name']
			cards[cardName] = row

	# open a json file handler and use json.dumps method to dump data
	with open(jsonPath, 'w', encoding='utf-8') as json_file_handler:
		json_file_handler.write(json.dumps(cards, indent=4))


def printWinRateGradesTable(jsonPath: str):
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
	with open(jsonPath) as file:
		data = json.load(file)

	# access the data from the JSON object
	# first create GIH WR array
	gameInHandWinRates: List[float] = []

	# CardName, GIH WR dictionary
	cardWinRates: Dict[str, float] = {}

	# iterate through JSON data to determine σ and μ for data set first
	for cardName in data.keys():
		# the data is actually in string format
		# so we need to do the following to convert to decimal:
		#   verify right-most char is '%'
		#   cast to float with 'e-2'

		# some cards don't have enough data and their GIH WR is empty: ''. so
		# we can simply ignore these in the data set, e.g.
		#   invasion of arcavios
		#   jin-gitaxias, core augur
		# alternatively we can try using "None", but this is untested
		winRateString: str = data[cardName]["GIH WR"]
		if winRateString != '':
			assert winRateString[-1] == '%'
			wr = float(winRateString.replace('%', 'e-2'))
			gameInHandWinRates.append(wr)
			cardWinRates[cardName] = wr
		else:
			cardWinRates[cardName] = None # test for None later when printing
			# print(f'!added: 🍆 {cardName}')

	# μ: float = statistics.mean(gameInHandWinRates)
	# σ: float = statistics.stdev(gameInHandWinRates)
	filteredWRs = [x for x in cardWinRates.values() if x is not None]

	μ: float = statistics.mean(filteredWRs)
	σ: float = statistics.stdev(filteredWRs)
	print(f'\nGIH WR μ → {μ}')
	print(f'GIH WR σ → {σ}\n')

	# calculate z-score using list comprehension: (data - μ) / σ
	# zScores: List[float] = [(x - μ) / σ for x in gameInHandWinRates]

	# now that we have the GIH WR σ and μ, display data:
	# note the JSON will be sorted however it was when the csv was requested
	# by default it will be by collector ID: alphabetical in wubrg order
	for cardName in data.keys():
		# some cards don't have data: check if it's actually in our GIHWR dict
		if cardName in cardWinRates:
			x: float = cardWinRates[cardName]  # GIH WR
			color: str = data[cardName]["Color"]
			rarity: str = data[cardName]["Rarity"]
			gradeStr = ' '  # empty space for alignment

			if x: # x is set to None if no GIH WR was available
				# calculate how many stdDevs away from the mean?
				zScore: float = (x - μ) / σ

				# iterate reversed gradeBounds list: ('A+', 2.17) ('B', 0.83)
				# if zScore is greater than current iterated value:
				# 	replace gradeStr with key: 'A+', 'B', etc.
				for gradePair in gradeBounds[::-1]:
					if zScore >= gradePair[1]:
						gradeStr = gradePair[0]

				print(
					f'{gradeStr:2} {zScore:7.3f} {cardWinRates[cardName]: 6.3f}'
					f' ← {rarity} [{color}] {cardName}')
			else:
				print(
					f'insufficient data: {rarity} [{color}] {cardName}')


# defines lower bound zScore values for letter grades like A-, D+, B, etc.
# each letter grade is one standard deviation, with C centered around the mean μ
# a list of tuples containing lower bounds for grades, e.g. S:2.5, A:1.83
# invariant: this is sorted by zScore value
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

# csvToJSON('ltr/2023-06-21.csv', 'ratings.json')
# csvToJSON('mom/card-ratings-2023-06-21.csv', 'ratings.json')
printWinRateGradesTable('ltr/2023.06.22-urlRequest.json')
