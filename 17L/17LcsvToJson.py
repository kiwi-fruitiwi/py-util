# from: askpython.com/python/examples/convert-csv-to-json
# purpose: convert 17L csv data into JSON format for 🚂17L-grades
# last ratings update: 2023.06.11: top, all colors

import csv
import json
import statistics
from typing import List


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
	gameInHandWinRates: List[str] = []
	for key in data.keys():
		# the data is actually in string format
		# so we need to do the following to convert to decimal:
		#   verify right-most char is '%'
		#   strip it
		#   convert to number
		#   divide by 100
		gameInHandWinRates.append(data[key]["GIH WR"])
		print(f'{key} → {data[key]["GIH WR"]}')

	print(gameInHandWinRates)


csvToJSON('ratings.csv', 'ratings.json')