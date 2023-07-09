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


def createMasterJson():
	# load all.json. this contains default data from 17L. it's the default page!
	defaultPath: str = f'data/ltr-CDP/all.json'
	with open(defaultPath, 'r', encoding='utf-8') as f:
		defaultJson = json.load(f)

	# iterate through every other colorPair, adding these data key,value pairs:
	#	#OH, OHWR, #GIH, GIHWR, IWD


def createStatsJson():
	"""
	open 📁data/ltr-CDP/all.json to calculate (μ,σ) for the default data set
		note we want to ignore data with sample size n<200
	repeat this for all colorPairs

	create a dictionary that we save into a json file, 📁statistics.json
		there will be the default mean and standard deviation floats
			'default μ': 0.558
			'default σ': 0.048
		followed by n pairs of μ, σ for each colorPair
			'WU μ': 0.547
			'WU σ':	0.043
		general format is:
			'{dataSetName} μ': 0.558
			'{dataSetName} σ': 0.048
	"""
	# open

	pass