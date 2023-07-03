# from: askpython.com/python/examples/convert-csv-to-json
# purpose: convert 17L csv data into JSON format for 🚂17L-grades

import csv
import json


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


csvToJSON('data/ltr/card-ratings-2023-07-03.csv', 'data/ratings.json')
# csvToJSON('mom/card-ratings-2023-06-21.csv', 'data/ratings.json')
