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
from constants import caliberRequestMap # top-players and all-players keys

# stats with low sample size not counted in μ,σ
from constants import minimumSampleSize, minOffColorSampleSize


dataSetBasePath: str = 'data/ltr-converted/'


# generates a dictionary mapping card names to their mana costs in format '2UUU'
# this makes things easier because scryfall json is not keyed by name.
def generateNameManacostDict(sfJson):
	# iterate through scryfallData. for each object:
	#   strip {} from castingCost in format "{4}{G}{W}"
	#   execute results[name] = strippedCastingCost
	# return results
	results: Dict[str, str] = {}
	for card in sfJson:
		# strip {}, converting {2}{W}{R} to 2WR
		manaCost: str = card['mana_cost'].replace("{", "").replace("}", "")
		name: str = card['name']
		results[name] = manaCost

	return results


# requires statistics.json to exist and be updated.
# needs scryfall.json to exist ← scryfall data for the entire set
# ⚠️ run createStatisticsJson first!
def createMasterJson(caliber: str):
	# load card info from scryfall json
	with open('data/scryfall.json', encoding='utf-8-sig') as f:
		scryfallJson = json.load(f)
		'''
		card data from scryfall, including oracle text and img links
		'''

	nameManacostDict: Dict = generateNameManacostDict(scryfallJson)

	# load all.json. this contains default data from 17L. it's the default
	# page! all.json is created and populated by requestConverter.py to
	# contain all necessary data for compareDraftPicks.py
	dataSetPath: str = f'{dataSetBasePath}{caliber}/all.json'
	with open(dataSetPath, 'r', encoding='utf-8') as jsonFileHandler:
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

	# for each cardName in the main json file, find its data in the colorPair
	# json files and append them. note we also need to remove default stats
	# entries and stuff them into a "🔑 all" key to represent 'all colors'
	for name, masterCardData in master.items():
		# stats we want z-scores for
		stats: List[str] = ['GIH WR', 'OH WR', 'GD WR', 'IWD']

		# create the filteredStats key with an empty dictionary we add to later
		masterCardData['filteredStats'] = {}
		zScores: Dict = createZscoreDict(masterCardData, stats, 'all', caliber)

		# add the 'all colors' data to this dictionary
		allStats: Dict = {
			'GIH WR': masterCardData['GIH WR'],
			'# GIH': masterCardData['# GIH'],
			'OH WR': masterCardData['OH WR'],
			'# OH': masterCardData['# OH'],
			'GD WR': masterCardData['GD WR'],
			'# GD': masterCardData['# GD'],
			'IWD': masterCardData['IWD'],

			# add zScores for GIH WR, OH WR, GD WR, and IWD
			'z-scores': zScores
		}

		masterCardData['filteredStats']['all'] = allStats

		# remove these keys from their original loc so data is not duplicated
		del masterCardData['GIH WR']
		del masterCardData['# GIH']
		del masterCardData['OH WR']
		del masterCardData['# OH']
		del masterCardData['GD WR']
		del masterCardData['# GD']
		del masterCardData['IWD']

		# grab the mana cost from our collapsed scryfall dictionary:
		# format is [cardName, mana cost] where latter is formatted
		# 1UUU instead of {1}{U}{U}{U}
		masterCardData['manaCost'] = nameManacostDict[name]

		# iterate through every colorPair, adding data in key,value pairs:
		# OH, OHWR, #GIH, GIHWR, #GD, GDWR, IWD, z-scores
		for colorPair in colorPairs:
			coloredJsonPath: str = f'{dataSetBasePath}{caliber}/{colorPair}.json'
			with open(coloredJsonPath, 'r', encoding='utf-8') as jsonFileHandler:
				coloredDataJson: Dict = json.load(jsonFileHandler)

			dataSetID: str = colorPair  # e.g. 'WU', 'UG'
			dataSetCardData: Dict = coloredDataJson[name]
			zScores: Dict = createZscoreDict(dataSetCardData, stats, dataSetID, caliber)

			# don't add colorStats data at all if '# GIH' doesn't meet sample
			# size requirement
			if dataSetCardData['# GIH'] < minOffColorSampleSize:
				pass
			else:
				colorPairStats: Dict = {
					'GIH WR': dataSetCardData['GIH WR'],
					'# GIH': dataSetCardData['# GIH'],
					'OH WR': dataSetCardData['OH WR'],
					'# OH': dataSetCardData['# OH'],
					'GD WR': dataSetCardData['GD WR'],
					'# GD': dataSetCardData['# GD'],
					'IWD': dataSetCardData['IWD'],
					'z-scores': zScores
				}

				masterCardData['filteredStats'][dataSetID] = colorPairStats

	# save the final master.json file
	with open(f'data/{caliber}Master.json', 'w', encoding='utf-8') as jsonSaver:
		jsonSaver.write(json.dumps(master, indent=4))

	print(f'🍑 master json saved → {caliber}')


def createZscoreDict(cardData: Dict, stats: List[str], dataSetID: str, caliber: str) -> Dict:
	"""
	create a dictionary with z-score values of the given input list
	:param cardData: one entry in master.json, keyed by cardName
	:param stats: a list of strings with stats we want z-scores for, e.g. OHWR
	:param dataSetID: 'all', 'WU', 'UG', etc. also known as colorPair str
	:return:
	"""
	# open the statistics data file to query for μ, σ
	jsonPath: str = f'data/{caliber}Stats.json'
	with open(jsonPath, 'r', encoding='utf-8') as statsFileHandler:
		cardStatistics: Dict = json.load(statsFileHandler)

	# 	statistics.json sample entry for one color pair, 'WU':
	'''
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
	# initialize the z-score dictionary we want to return
	zScoreResults: Dict = {}

	# iterate through a list of stats we want z-scores for, e.g. 'all', 'WU'
	for stat in stats:
		zScore: float = getZscore(
			cardData[stat],
			dataSetID,
			stat,
			cardStatistics)

		zScoreResults[stat] = zScore
	return zScoreResults


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

	if statValue is None:
		return None
	return (statValue - mean) / stdDev


def createStatsJson(caliber: str):
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
	calculateAndAddStatsKeyValuePairs('all', f'{dataSetBasePath}{caliber}/all.json', result)

	# second, iterate through all other dataSets after encapsulating step 1
	for colorPair in colorPairs:
		dataSetPath: str = f'{dataSetBasePath}{caliber}/{colorPair}.json'
		calculateAndAddStatsKeyValuePairs(colorPair, dataSetPath, result)

	# [print(f'{key}: {value}') for (key, value) in result.items()]

	# lastly, save the json file for access later
	with open(f'data/{caliber}Stats.json', 'w', encoding='utf-8') as jsonSaver:
		jsonSaver.write(json.dumps(result, indent=4))

	print(f'🥭 statistics json saved → {caliber}')


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

	# TODO sometimes this will raise statisticsError if one of the 4 lists is
	# 	empty. the workaround is to increase the minimum sample size constant
	# 	but this should really check for emptiness.
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


def main():
	# all-players vs top-players
	for caliber in caliberRequestMap.keys():
		createStatsJson(caliber)
		createMasterJson(caliber)


main()