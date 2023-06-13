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
			key = row['Name']
			cards[key] = row
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

	for key in data.keys():
		# print(f'{key} → {data[key]["GIH WR"]}')

		# the data is actually in string format
		# so we need to do the following to convert to decimal:
		#   verify right-most char is '%'
		#   cast to float with 'e-2'

		# some cards don't have enough data and their GIH WR is empty: ''. so
		# we simply ignore these in the data set, e.g.
		#   invasion of arcavios
		#   jin-gitaxias, core augur
		winRateString: str = data[key]["GIH WR"]
		if winRateString != '':
			assert winRateString[-1] == '%'
			wr = float(winRateString.replace('%', 'e-2'))
			gameInHandWinRates.append(wr)
			cardWinRates[key] = wr
		else:
			print(f'!added: 🍆 {key}')

	# print(gameInHandWinRates)
	μ: float = statistics.mean(gameInHandWinRates)
	σ: float = statistics.stdev(gameInHandWinRates)
	print(f'GIH WR μ → {μ}')
	print(f'GIH WR σ → {σ}')

	# calculate z-score: (data - μ) / σ
	zScores: List[float] = [(x - μ) / σ for x in gameInHandWinRates]
	# print(zScores)

	# display cardName, GIH WR pairs
	# for key in cardWinRates.keys():
	# print(f'z: {cardWinRates[key]: .3f} ← {key}')

	# create cardName, zScore dictionary
	cardNamesAndZScores: Dict[str, float] = {}
	for name in cardWinRates.keys():
		x: float = cardWinRates[name]
		zScore: float = (x - μ) / σ
		zStr = ' ' # empty space for alignment

		# set letter grade based on zScore range
		match zScore:
			case n if Grade.S.value <= n < Grade.CEILING.value:
				zStr = 'S'
			case n if Grade.A_PLUS.value <= n < Grade.S.value:
				zStr = 'A+'
			case n if Grade.A.value <= n < Grade.A_PLUS.value:
				zStr = 'A'
			case n if Grade.A_MINUS.value <= n < Grade.A.value:
				zStr = 'A-'

			case n if Grade.B_PLUS.value <= n < Grade.A_MINUS.value:
				zStr = 'B+'
			case n if Grade.B.value <= n < Grade.B_PLUS.value:
				zStr = 'B'
			case n if Grade.B_MINUS.value <= n < Grade.B.value:
				zStr = 'B-'

			case n if Grade.C_PLUS.value <= n < Grade.B_MINUS.value:
				zStr = 'C+'
			case n if Grade.C.value <= n < Grade.C_PLUS.value:
				zStr = 'C'
			case n if Grade.C_MINUS.value <= n < Grade.C.value:
				zStr = 'C-'

			case n if Grade.D_PLUS.value <= n < Grade.C_MINUS.value:
				zStr = 'D+'
			case n if Grade.D.value <= n < Grade.D_PLUS.value:
				zStr = 'D'
			case n if Grade.D_MINUS.value <= n < Grade.D.value:
				zStr = 'D-'

			case n if n < Grade.D_MINUS.value:
				zStr = 'F'


		print(f'{zStr:2} {zScore:7.3f} {cardWinRates[name]: 6.3f} ← {name}')


# defines lower bound zScore values for letter grades like A-, D+, B, etc.
# each letter grade is one standard deviation, with C centered around the mean μ
class Grade(Enum):
	CEILING = 10 # 10 is arbitrary impossibly high stddev
	S = 2.5

	A_PLUS = 2.17
	A = 1.83
	A_MINUS = 1.5

	B_PLUS = 1.17
	B = 0.83
	B_MINUS = 0.5

	C_PLUS = 0.17
	C = -0.17
	C_MINUS = -0.5

	D_PLUS = -0.83
	D = -1.17
	D_MINUS = -1.5

	F = -1 * CEILING



csvToJSON('ratings.csv', 'ratings.json')
