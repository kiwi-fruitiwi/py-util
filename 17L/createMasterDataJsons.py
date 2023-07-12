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


# requires statistics.json to exist and be updated.
# ⚠️ run createStatisticsJson first!
def createMasterJson():
	# load default.json. this contains default data from 17L. it's the default
	# page! default.json is created and populated by requestConverter.py to
	# contain all necessary data for compareDraftPicks.py
	defaultPath: str = f'data/ltr-CDP/default.json'
	with open(defaultPath, 'r', encoding='utf-8') as jsonFileHandler:
		master: Dict = json.load(jsonFileHandler)

	'''
	dataSet entries look like this:
		"Birthday Escape": {
			"Name": "Birthday Escape",
			"ALSA": 4.73890697755838,
			"ATA": 5.9463545685786965,
			"# OH": 30503,
			"OH WR": 0.5754188112644658,
			"# GD": 56190,
			"GD WR": 0.6073322655276739,
			"# GIH": 86693,
			"GIH WR": 0.5961034916313889,
			"IWD": 0.06817131686181177,
			"URL": "https://cards.scryfall.io/border_crop/front/4/...",
			"Color": "U",
			"Rarity": "C"
		},
	'''

	# open the statistics data file to query for μ, σ
	jsonPath: str = f'data/statistics.json'
	with open(jsonPath, 'r', encoding='utf-8') as statsFileHandler:
		cardStatistics: Dict = json.load(statsFileHandler)

	'''
	statistics.json sample entry for one color pair, 'WU':
		"WU": {
			"GIH WR": {
				"mean": 0.5488155671189182,
				"stdDev": 0.040161553535718666
			},
			"OH WR": {
				"mean": 0.5202702618891792,
				"stdDev": 0.04189691189749475
			},
			"IWD": {
				"mean": 0.061524972063645815,
				"stdDev": 0.04081348580719822
			}
		},
	'''

	# for each cardName in the main json file, find its data in the colorPair
	# json files and append them. note we also need to remove default stats
	# entries and stuff them into a "🔑 default" key
	for name, data in master.items():
		# iterate through every colorPair, adding data in key,value pairs:
		# OH, OHWR, #GIH, GIHWR, IWD

		# create the filteredStats key with an empty dictionary we add to later
		data['filteredStats'] = {}

		# prepare to calculate z-scores for 'GIH WR', 'OH WR', 'GD WR' and 'IWD'
		# z-score is calculated (x-μ)/σ where x is the data point

		cardGihwr: float = data['GIH WR']
		defaultGihwrMean: float = cardStatistics['default']['GIH WR']['mean']
		defaultGihwrStdDev: float = cardStatistics['default']['GIH WR']['stdDev']
		defaultGihwrZscore: float = \
			(cardGihwr-defaultGihwrMean) / defaultGihwrStdDev

		# add the "default", all colors data to this dictionary
		# remove these keys from their original loc so data is not duplicated
		defaultStats: Dict = {
			'GIH WR': data['GIH WR'],
			'# GIH': data['# GIH'],
			'OH WR': data['OH WR'],
			'# OH': data['# OH'],
			'GD WR': data['GD WR'],
			'# GD': data['# GD'],
			'IWD': data['IWD']

			# add zScores for GIH WR, OH WR, GD WR, and IWD

		}

		data['filteredStats']['default'] = defaultStats

		del data['GIH WR']
		del data['# GIH']
		del data['OH WR']
		del data['# OH']
		del data['GD WR']
		del data['# GD']
		del data['IWD']

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
				'# GIH': currentDataSetCardData['# GIH'],
				'OH WR': currentDataSetCardData['OH WR'],
				'# OH': currentDataSetCardData['# OH'],
				'GD WR': currentDataSetCardData['GD WR'],
				'# GD': currentDataSetCardData['# GD'],
				'IWD': currentDataSetCardData['IWD']
			}

			data['filteredStats'][dataSetID] = colorPairStats



	# for cardName, cardData in master.items():
	#	[print(f'{key}: {value}') for (key, value) in cardData.items()]
	with open(f'data/master.json', 'w', encoding='utf-8') as jsonSaver:
		jsonSaver.write(json.dumps(master, indent=4))

	print(f'🍑 master json saved')


def getZscore(statValue: float, dataSetStr: str, statKey: str, statisticsJson: Dict) -> float:
	"""
	returns the z-score
	:param statValue: our data value, e.g. GIH WR for a card
	:param dataSetStr: 'default', 'WU', 'UG', etc.
	:param statKey: 'GIH WR'
	:param statisticsJson: the json file created by createStatsJson
	:return:
	"""
	mean: float = statisticsJson[dataSetStr][statKey]['mean']
	stdDev: float = statisticsJson[dataSetStr][statKey]['stdDev']
	return (statValue - mean) / stdDev


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
	gdwrList: List[float] = []
	iwdList: List[float] = []

	# calculate μ, σ, noting we don't factor in low sample size
	for cardName in dataSet.keys():
		card: Dict = dataSet[cardName]

		gamesSeenGIH: int = card['# GIH']
		if gamesSeenGIH < minimumSampleSize:
			# don't let this factor into calculations for mean and stdDev
			pass
		else:
			# note that improvement-when-drawn, or IWD, has its sample size
			# linked to game-in-hand
			gihwrList.append(card['GIH WR'])
			iwdList.append(card['IWD'])

		gamesSeenOH: int = card['# OH']
		if gamesSeenOH < minimumSampleSize:
			# skip this data point
			pass
		else:
			ohwrList.append(card['OH WR'])
			
		gamesSeenGD: int = card['# GD']
		if gamesSeenGD < minimumSampleSize:
			pass
		else:
			gdwrList.append(card['GD WR'])

	colorPairStats: Dict = {
		'GIH WR': {
			'mean': statistics.mean(gihwrList),
			'stdDev': statistics.stdev(gihwrList)
		},
		'OH WR': {
			'mean': statistics.mean(ohwrList),
			'stdDev': statistics.stdev(ohwrList)
		},
		'GD WR': {
			'mean': statistics.mean(gdwrList),
			'stdDev': statistics.stdev(gdwrList)
		},
		'IWD': {
			'mean': statistics.mean(iwdList),
			'stdDev': statistics.stdev(iwdList)
		}
	}

	statsDictionary[dataSetID] = colorPairStats


createStatsJson()
createMasterJson()