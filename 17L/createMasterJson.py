# start with all.json, created via requestConverter.py from the default 17L
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
	# load all.json. this contains default data from 17L. it's the default page!
	# all.json is created and populated by requestConverter.py to contain all
	# necessary data for compareDraftPicks.py
	defaultPath: str = f'data/ltr-CDP/all.json'
	with open(defaultPath, 'r', encoding='utf-8') as f:
		dataSet: Dict = json.load(f)

	# dataSet entries look like this:
	# "Bill the Pony": {
	#     "Name": "Bill the Pony",
	#     "ALSA": 3.486085617857777,
	#     "ATA": 4.213059170950454,
	#     "# OH": 43,
	#     "OH WR": 0.6046511627906976,
	#     "# GIH": 97,
	#     "GIH WR": 0.6288659793814433,
	#     "IWD": 0.1502945508100147,
	#     "URL": "https://cards.scryfall.io/border_crop/front...,
	#     "Color": "W",
	#     "Rarity": "U"
	# },




	# iterate through every other colorPair, adding these data key,value pairs:
	#	OH, OHWR, #GIH, GIHWR, IWD
	pass


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

	# first, find the μ,σ pair for the default data set
	defaultPath: str = f'data/ltr-CDP/all.json'
	with open(defaultPath, 'r', encoding='utf-8') as f:
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

	print(f'🥝GIH: μ={μ_gihwr} σ={σ_gihwr}')
	print(f'🥝OH: μ={μ_ohwr} σ={σ_ohwr}')
	print(f'🥝IWD: μ={μ_iwd} σ={σ_iwd}')

	result["default GIHWRμ"] = μ_gihwr
	result["default GIHWRσ"] = σ_gihwr
	result["default OHWRμ"] = μ_ohwr
	result["default OHWRσ"] = σ_ohwr
	result["default IWDμ"] = μ_iwd
	result["default IWDσ"] = σ_iwd

	[print(f'{key}: {value}') for (key, value) in result.items()]


	# second, iterate through all other dataSets after encapsulating step 1
	inputJsonPath: str = f'data/ltr-CDP/'
	for colorPair in colorPairs:
		dataSetPath: str = f'{inputJsonPath}{colorPair}.json'
		print(f'{dataSetPath}')


	# lastly, save the json file for access later


createMasterJson()
createStatsJson()