# from: askpython.com/python/examples/convert-csv-to-json

import csv
import json


def csv_to_json(csvPath, jsonPath):
	# create a dictionary
	data_dict = {}

	# Step 2
	# open a csv file handler
	with open(csvPath, encoding='utf-8') as csv_file_handler:
		csv_reader = csv.DictReader(csv_file_handler)

		# convert each row into a dictionary
		# and add the converted data to the data_variable

		for rows in csv_reader:
			# primary key is the name of the file, 0
			key = rows[0]
			data_dict[key] = rows

	# open a json file handler and use json.dumps
	# method to dump the data
	# Step 3
	with open(jsonPath, 'w', encoding='utf-8') as json_file_handler:
		# Step 4
		json_file_handler.write(json.dumps(data_dict, indent=4))


# driver code
# be careful while providing the path of the csv file
# provide the file path relative to your machine

# Step 1
csv_file_path = input('Enter the absolute path of the CSV file: ')
json_file_path = input('Enter the absolute path of the JSON file: ')

csv_to_json(csv_file_path, json_file_path)