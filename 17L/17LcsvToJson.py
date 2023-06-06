# from: askpython.com/python/examples/convert-csv-to-json
# purpose: convert 17L csv data into JSON format for 🚂17Lgrades

import csv
import json


def csv_to_json(csvPath, jsonPath):
	# create a dictionary
	data_dict = {}

	# Step 2
	# open a csv file handler
	with open(csvPath, encoding='utf-8-sig') as csv_file_handler:
		csv_reader = csv.DictReader(csv_file_handler)

		# convert each row into a dictionary
		# and add the converted data to the data_variable

		for row in csv_reader:
			# primary key is the name of the file, 0
			key = row['Name']
			data_dict[key] = row
			# print(f'{key}')

			print(f'{row}')

	# open a json file handler and use json.dumps
	# method to dump the data
	# Step 3
	with open(jsonPath, 'w', encoding='utf-8') as json_file_handler:
		# Step 4
		json_file_handler.write(json.dumps(data_dict, indent=4))


csv_to_json('ratings.csv', 'ratings.json')