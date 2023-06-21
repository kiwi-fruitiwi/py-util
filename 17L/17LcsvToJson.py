# from: askpython.com/python/examples/convert-csv-to-json
# purpose: convert 17L csv data into JSON format for 🚂17L-grades
# last ratings update: 2023.06.11: top, all colors

import csv
import json
import statistics
from typing import List, Dict
from enum import Enum


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
	# print(f'{key}')

	# open a json file handler and use json.dumps method to dump data
	with open(jsonPath, 'w', encoding='utf-8') as json_file_handler:
		json_file_handler.write(json.dumps(cards, indent=4))

	# it's time to actually read the JSON we created
	with open(jsonPath) as file:
		# Load the JSON data from the file
		data = json.load(file)

	# access the data from the JSON object
	# first create GIH WR array
	gameInHandWinRates: List[float] = []

	# CardName, GIH WR dictionary
	cardWinRates: Dict[str, float] = {}

	for cardName in data.keys():
		# print(f'{key} → {data[key]["GIH WR"]}')

		# the data is actually in string format
		# so we need to do the following to convert to decimal:
		#   verify right-most char is '%'
		#   cast to float with 'e-2'

		# some cards don't have enough data and their GIH WR is empty: ''. so
		# we simply ignore these in the data set, e.g.
		#   invasion of arcavios
		#   jin-gitaxias, core augur
		winRateString: str = data[cardName]["GIH WR"]
		if winRateString != '':
			assert winRateString[-1] == '%'
			wr = float(winRateString.replace('%', 'e-2'))
			gameInHandWinRates.append(wr)
			cardWinRates[cardName] = wr
		else:
			print(f'!added: 🍆 {cardName}')

	# print(gameInHandWinRates)
	μ: float = statistics.mean(gameInHandWinRates)
	σ: float = statistics.stdev(gameInHandWinRates)
	print(f'GIH WR μ → {μ}')
	print(f'GIH WR σ → {σ}')

	# calculate z-score using list comprehension: (data - μ) / σ
	zScores: List[float] = [(x - μ) / σ for x in gameInHandWinRates]

	# now that we have the GIH WR σ and μ, display data:
	# some cards don't have data, so we check if it's actually in our GIHWR dict
	for cardName in data.keys():
		if cardName in cardWinRates:
			x: float = cardWinRates[cardName]  # GIH WR
			zScore: float = (x - μ) / σ  # how many stdDevs away from the mean?
			gradeStr = ' '  # empty space for alignment

			# iterate through reversed list
			# if zScore is greater than current iterated value:
			# 	replace gradeStr with key
			for gradePair in gradeBounds[::-1]:
				if zScore >= gradePair[1]:
					gradeStr = gradePair[0]

			color: str = data[cardName]["Color"]
			rarity: str = data[cardName]["Rarity"]

			print(f'{gradeStr:2} {zScore:7.3f} {cardWinRates[cardName]: 6.3f}'
				  f' ← {rarity} [{color}] {cardName}')


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

csvToJSON('ltr/2023-06-21.csv', 'ratings.json')
