# start with default.json, created via requestConverter.py from the default 17L
# request. this is keyed by 🔑:cardName
#
# add the following information from all n colorPairs:
# 	'# OH'
# 	'OH WR'
# 	'# GIH'
# 	'GIH WR'
# 	'IWD'
# -suffixed with the colorPair string, e.g. 'WU', 'UG', 'WR'
# then this will be 'master.json' under 📁 data/

import json
import statistics
from typing import Dict, List
from constants import colorPairs  # WU, UG, WR, etc.

# stats with low sample size not counted in μ,σ
from constants import minimumSampleSize


def createMasterJson():
	# load default.json. this contains default data from 17L. it's the default
	# page! default.json is created and populated by requestConverter.py to
	# contain all necessary data for compareDraftPicks.py
	defaultPath: str = f'data/ltr-CDP/default.json'
	with open(defaultPath, 'r', encoding='utf-8') as jsonFileHandler:
		master: Dict = json.load(jsonFileHandler)

	'''
	dataSet entries look like this:
		"Bill the Pony": {
		    "Name": "Bill the Pony",
		    "ALSA": 3.486085617857777,
		    "ATA": 4.213059170950454,
		    "# OH": 43,
		    "OH WR": 0.6046511627906976,
		    "# GIH": 97,
		    "GIH WR": 0.6288659793814433,
		    "IWD": 0.1502945508100147,
		    "URL": "https://cards.scryfall.io/border_crop/front...,
		    "Color": "W",
		    "Rarity": "U"
	},
	'''


	# for each cardName in the main json file, find its data in the colorPair
	# json files and append them
	for name, data in master.items():
		# iterate through every colorPair, adding data in key,value pairs:
		# OH, OHWR, #GIH, GIHWR, IWD

		# create the filteredStats key with an empty dictionary we add to later
		data['filteredStats'] = {}

		for colorPair in colorPairs:
			coloredJsonPath: str = f'data/ltr-CDP/{colorPair}.json'
			with open(coloredJsonPath, 'r', encoding='utf-8') as jsonFileHandler:
				currentDataSet: Dict = json.load(jsonFileHandler)

			dataSetID: str = colorPair  # e.g. 'WU', 'UG'
			cardData: Dict = data  # master[name] is a Dict containing one card
			currentDataSetCardData: Dict = currentDataSet[name]

			# append new key,value pair to master[name]'s value
			# create a "filteredStats" dictionary we will append later
			# it will contain the 5 stats as values as the colorPair as a 🔑key
			# we need: '# OH', 'OH WR', '# GIH', 'GIH WR', 'IWD'
			colorPairStats: Dict = {
				'GIH WR': currentDataSetCardData['GIH WR'],
				'OH WR': currentDataSetCardData['OH WR'],
				'# GIH': currentDataSetCardData['# GIH'],
				'# OH': currentDataSetCardData['# OH'],
				'IWD': currentDataSetCardData['IWD']
			}

			data['filteredStats'][colorPair] = colorPairStats



	# for cardName, cardData in master.items():
	#	[print(f'{key}: {value}') for (key, value) in cardData.items()]
	with open(f'data/master.json', 'w', encoding='utf-8') as jsonSaver:
		jsonSaver.write(json.dumps(master, indent=4))

	print(f'🍑 master json saved')


def createStatsJson():
	"""
	open 📁data/ltr-CDP/all.json to calculate (μ,σ) for the default data set
		note we want to ignore data with sample size n<200
	repeat this for all colorPairs

	create a dictionary that we save into a json file, 📁statistics.json
		there will be the default mean and standard deviation floats
			'default GIHWRμ': 0.557879835393347
			'default GIHWRσ': 0.047812878277838505
			'default OHWRμ': 0.5442907414746199
			'default OHWRσ': 0.05669897307759159
			'default IWDμ': 0.030778505972504082
			'default IWDσ': 0.039418556991144896
		followed by n pairs of μ, σ for each colorPair for each of three stats
			'WU μ': 0.547
			'WU σ':	0.043
		general format is:
			'{dataSetName} μ': 0.558
			'{dataSetName} σ': 0.048
	"""
	# dictionary we will save to json
	result: Dict = {}

	# find μ, σ stats for default data set: all.json
	calculateAndAddStatsKeyValuePairs(
		'default', 'data/ltr-CDP/default.json', result)

	# second, iterate through all other dataSets after encapsulating step 1
	inputJsonPath: str = f'data/ltr-CDP/'
	for colorPair in colorPairs:
		dataSetPath: str = f'{inputJsonPath}{colorPair}.json'
		calculateAndAddStatsKeyValuePairs(colorPair, dataSetPath, result)

	# [print(f'{key}: {value}') for (key, value) in result.items()]

	# lastly, save the json file for access later
	with open(f'data/statistics.json', 'w', encoding='utf-8') as jsonSaver:
		jsonSaver.write(json.dumps(result, indent=4))

	print(f'🥭 statistics json saved')


# calculate (μ,σ) pairs for GIHWR, OHWR, and IWD from the json file specified at
# dataSetPath. add them to input dictionary
def calculateAndAddStatsKeyValuePairs(
		dataSetID: str, dataSetPath: str, statsDictionary: Dict):
	with open(dataSetPath, 'r', encoding='utf-8') as f:
		dataSet: Dict = json.load(f)

	gihwrList: List[float] = []
	ohwrList: List[float] = []
	iwdList: List[float] = []

	# calculate μ, σ, noting we don't factor in low sample size
	for cardName in dataSet.keys():
		card: Dict = dataSet[cardName]

		gamesSeenGIH: int = card["# GIH"]
		if gamesSeenGIH < minimumSampleSize:
			# don't let this factor into calculations for mean and stdDev
			pass
		else:
			# note that improvement-when-drawn, or IWD, has its sample size
			# linked to game-in-hand
			gihwrList.append(card["GIH WR"])
			iwdList.append(card["IWD"])

		gamesSeenOH: int = card["# OH"]
		if gamesSeenOH < minimumSampleSize:
			# skip this data point
			pass
		else:
			ohwrList.append(card["OH WR"])

	μ_gihwr: float = statistics.mean(gihwrList)
	σ_gihwr: float = statistics.stdev(gihwrList)
	μ_ohwr: float = statistics.mean(ohwrList)
	σ_ohwr: float = statistics.stdev(ohwrList)
	μ_iwd: float = statistics.mean(iwdList)
	σ_iwd: float = statistics.stdev(iwdList)

	colorPairStats: Dict = {
		"GIHWR_mean": μ_gihwr,
		"GIHWR_stdDev": σ_gihwr,
		"OHWR_mean": μ_ohwr,
		"OHWR_stdDev": σ_ohwr,
		"IWD_mean": μ_iwd,
		"IWD_stdDev": σ_iwd
	}

	statsDictionary[dataSetID] = colorPairStats


createMasterJson()
createStatsJson()