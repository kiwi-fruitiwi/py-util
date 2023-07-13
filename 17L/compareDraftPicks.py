import Levenshtein  # makes finding the L-distance between strings much faster
import json
import statistics

from fuzzywuzzy import process
from typing import List, Dict
from scryfallCardFetch import printCardText
from constants import colorPairs, minimumSampleSize

# defines lower bound zScore values for letter grades like A-, D+, B, etc.
# each letter grade is one standard deviation, with C centered around the mean μ
# a list of tuples containing lower bounds for grades, e.g. S:2.5, A:1.83
# invariant: this is sorted by zScore value
gradeBounds: List[tuple] = [
	('S+', 3.0),
	('S', 2.5),
	('A+', 2.17),
	('A', 1.83),
	('A-', 1.5),
	('B+', 1.17),
	('B', 0.83),
	('B-', 0.5),
	('C+', 0.17),
	('C', 0),
	('C-', -0.17),
	('D+', -0.83),
	('D', -1.17),
	('D-', -1.5),
	('F', -10)
]


MIN_SAMPLE_SIZE: int = 200


# if we're only comparing one card, skip newlines so subsequent queries
# are easier to visually compare
compareOne: bool = False
displayIwdGrade: bool = False
displayCardFetchList: bool = False
displayGihOhDiff: bool = True  # difference in zScore between GIH and OH WRs
displayOhZscore: bool = True
displayRarityAndMv: bool = False

dataSetUri: str = 'data/master.json'


# main input loop to ask for user input → return list of card stats
# main includes
# 	the input logic: `!` and `colorPair: ` prefixes
# 	performs fuzzy matching on card names
# 	calls **printCardData** using the selected colorPair json file
# 	(or the default all colors file)
def main():
	# load card info from scryfall json
	with open('data/scryfall.json', encoding='utf-8-sig') as f:
		scryfallJson = json.load(f)
		'''
		card data from scryfall, including oracle text and img links
		'''

	# load aggregated master data
	with open(dataSetUri) as file:
		masterJson: Dict = json.load(file)
		'''
		master.json, aggregated data set from 17L with 'all' and colorPair data
		
		"Mushroom Watchdogs": {
        "Name": "Mushroom Watchdogs",
        "ALSA": 6.540190935273274,
        "ATA": 9.316888800477422,
        "URL": "https://cards.scryfall.io/border_crop/front/d/1/d15fd66d-fa7e-411d-9014-a56caa879d93.jpg?1685475587",
        "Color": "G",
        "Rarity": "C",
        "filteredStats": {
            "all": {
                "GIH WR": 0.5307067390663804,
                "# GIH": 23757,
                "OH WR": 0.5347051294673624,
                "# OH": 10157,
                "GD WR": 0.5277205882352941,
                "# GD": 13600,
                "IWD": 0.01449355618653092,
                "z-scores": {
                    "GIH WR": -0.6087595880909483,
                    "OH WR": -0.26421759784763266,
                    "GD WR": -0.9673573311007,
                    "IWD": -0.4456916782217906
                }
            },
            "WG": {
                "GIH WR": 0.5320304968889668,
                "# GIH": 11411,
                "OH WR": 0.5375103050288541,
                "# OH": 4852,
                "GD WR": 0.5279768257356304,
                "# GD": 6559,
                "IWD": 0.020120355516556998,
                "z-scores": {
                    "GIH WR": -0.1501275360237784,
                    "OH WR": 0.37914599272031013,
                    "GD WR": -0.6613069872127326,
                    "IWD": -0.3508266920392758
                }
            },
		'''

	# open the statistics data file to query for μ, σ
	jsonPath: str = f'data/statistics.json'
	with open(jsonPath, 'r', encoding='utf-8') as statsFileHandler:
		cardStatistics: Dict = json.load(statsFileHandler)
		'''
		statistics data
		
		"WU": {
			"GIH WR": {
				"mean": 0.5481773664431846,
				"stdDev": 0.0396680728733385
			},
			"OH WR": {
				"mean": 0.5200756145211735,
				"stdDev": 0.04154648783076403
			},
			"GD WR": {
				"mean": 0.56087617869494,
				"stdDev": 0.0389425738105168
			},
			"IWD": {
				"mean": 0.06100664189146016,
				"stdDev": 0.04077503221641616
			}
		},
		'''

	nameManacostDict: Dict = generateNameManacostDict(scryfallJson)

	global compareOne
	global displayCardFetchList

	done: bool = False

	while not done:
		printFlag = False
		if not compareOne:
			print('')
		userInput: str = input('Enter cards: ')

		# split the input string into a list using ',' as delimiter
		names: List[str] = userInput.split(',')

		# trim leading and trailing whitespace
		values: List[str] = [name.strip() for name in names]

		# special command: print card text if first char is '!'
		# this is done only if there's one card name in the input
		firstElement: str = values[0]
		if firstElement[0] == '!':
			printFlag: bool = True
			updatedFirstElement = firstElement[1:].strip()  # remove the '!'
			values[0] = updatedFirstElement  # clobber to update value

		firstElement: str = values[0]  # updated, after '!' is stripped
		# check if first element contains ':' if so, split(':')
		# use this to determine what json file we'll be loading
		dataSetID: str = f'all'

		# special command: colorPair with colon, e.g. 'WU: '
		# 	this will open data from the corresponding file and save to json17L
		#    how do we access 17LdataFetch colorPair?
		#    load the color pair json that corresponds to it
		# strip after in case there are multiple spaces after 'WU:'
		if ':' in firstElement:
			tokens: List[str] = firstElement.split(':')

			# there should be only two tokens: colorPair: cardName
			# and colorPair must be in [WU, WB, WR, WG, etc.]
			assert len(tokens) == 2
			assert tokens[0].upper() in colorPairs

			# save what our current data set is so it's visible with the data
			# note it's either the default "all colors" json or one of the
			# colorPairs: WU WB WR WG etc.
			dataSetID = tokens[0].upper()
			values[0] = values[0].strip()

		# set up list of card names matched to our input
		cardFetchList: List[str] = []

		for value in values:
			# extractOne returns a tuple like this: ('Arwen Undómiel', 90)
			# we're just interested in the name, not the closeness
			bestMatch = process.extractOne(value, masterJson.keys())

			if bestMatch:
				bestMatchName = bestMatch[0]
				cardFetchList.append(bestMatchName)
			else:
				print(f'🍆 best match not found for {value}')

		# if there's only one card, we will show how it performs overall as well
		# as in each color pair!
		if len(cardFetchList) == 1:
			cardName: str = cardFetchList[0]
			printArchetypesData(cardName, masterJson[cardName])
		else:
			compareOne = False  # use newlines to reduce clutter for big tables
			# print a list of names if we're matching more than one card
			if displayCardFetchList:
				[print(name) for name in cardFetchList]
			printCardComparison(
				masterJson,
				cardStatistics,
				cardFetchList,
				nameManacostDict,
				dataSetID
			)
			# printCardData(cardFetchList, nameManacostDict, dataSetStr)

		# if there's only one card name input and it's preceded by '!'
		# → print the card's spoiler text
		# recall that printFlag is set when user input is prefixed with '!'
		if printFlag and len(cardFetchList) == 1:
			printCardText(cardFetchList[0], scryfallJson)


def getGrade(zScore: float):
	letterGrade: str = ''

	# iterate reversed gradeBounds list: ('A+', 2.17) ('B', 0.83)
	# if zScore is greater than current iterated value:
	# 	replace gradeStr with key: 'A+', 'B', etc.
	for gradePair in gradeBounds[::-1]:
		if zScore >= gradePair[1]:
			letterGrade = gradePair[0]
	return letterGrade


def printArchetypesData(cardName: str, cardStats: Dict):
	"""

	:param cardName:
	:param cardStats: json containing data for a single card
	:return:
	"""

	# header: display columns and title above the colorPairStrs
	print(f'💦 {cardName} → ALSA {cardStats["ALSA"]:.1f}')
	print(
		f'     n '		# # GIH: sample size
		f'| '			# outer column
		f'   ' 			# colorPair: 2 char + 1 space
		f'|  ' 			# ' → '
		f'   ' 			# ohwrGrade: 2 char + 1 space
		f'    '			# OH z-score: 5 char + 1 space, e.g. '-1.50'
		f'   OH'		# ohwr: 4 char + 1 space, e.g. 54.8
		f' |  '			# column break
		f'   ' 			# gdwrGrade: 2 char + 1 space
		f'    '			# GD z-score
		f'   GD'		# gdwr: 4 char + 1 space
		f' |  '			# column break
		f'   ' 			# iwdGrade: 2 char + 1 space
		f'    '			# IWD z-score
		f'    IWD'		# IWD: 4 char + 1 space, e.g. -15.2pp
	)

	# iterate through colorPairs data to display the following stats:
	# OH WR, OH WR z-score
	# GD WR, GD WR z-score
	# IWD
	# include the colorPairStr
	# ✒️ ALSA likely not necessary
	stats: Dict = cardStats['filteredStats']
	for colorPair in colorPairs:
		if colorPair in stats:
			colorStats: Dict = stats[colorPair]
			# output the data we want for each colorPair
			ohwr: float = colorStats['OH WR']
			zOhwr: float = colorStats['z-scores']['OH WR']
			ohwrGrade: str = getGrade(zOhwr)

			gdwr: float = colorStats['GD WR']
			zGdwr: float = colorStats['z-scores']['GD WR']
			gdwrGrade: str = getGrade(zGdwr)

			iwd: float = colorStats['IWD']
			zIwd: float = colorStats['z-scores']['IWD']
			iwdGrade: str = getGrade(zIwd)

			print(
				f'{colorStats["# GIH"]:6} '
				f'| '
				f'{colorPair} | '
				f'{ohwrGrade:2} {zOhwr:>5.2f} {ohwr*100:4.1f}'
				f' | '
				f'{gdwrGrade:2} {zGdwr:>5.2f} {gdwr*100:4.1f}'
				f' | '
				f'{iwdGrade:2} {zIwd:>5.2f} {iwd*100:4.1f}pp'
			)
	pass


	'''
	sample json data from master.json
	"Mushroom Watchdogs": {
    "Name": "Mushroom Watchdogs",
    "ALSA": 6.540190935273274,
    "ATA": 9.316888800477422,
    "URL": "https://cards.scryfall.io/border_crop/...
    "Color": "G",
    "Rarity": "C",
    "filteredStats": {
		"all": {
			"GIH WR": 0.5307067390663804,
			"# GIH": 23757,
			"OH WR": 0.5347051294673624,
			"# OH": 10157,
			"GD WR": 0.5277205882352941,
			"# GD": 13600,
			"IWD": 0.01449355618653092,
			"z-scores": {
				"GIH WR": -0.6087595880909483,
				"OH WR": -0.26421759784763266,
				"GD WR": -0.9673573311007,
				"IWD": -0.4456916782217906
			}
		},
		"WG": {
			"GIH WR": 0.5320304968889668,
			"# GIH": 11411,
			"OH WR": 0.5375103050288541,
			"# OH": 4852,
			"GD WR": 0.5279768257356304,
			"# GD": 6559,
			"IWD": 0.020120355516556998,
			"z-scores": {
				"GIH WR": -0.1501275360237784,
				"OH WR": 0.37914599272031013,
				"GD WR": -0.6613069872127326,
				"IWD": -0.3508266920392758
			}
		}, 
	'''


def printCardComparison(
		masterData: Dict,			# masterJson[cardName]
		statsData: Dict,			# statisticsJson[dsID]
		cardNameList: List[str],	# fuzzy input matching results
		nameManacostDict,
		dataSetID: str,				# 'all', 'WU', 'UG', 'RG'
	):

	# sorts master.json data according to one stat, e.g. 'GD WR', 'OH WR'
	def statSortKey(item, stat: str):
		data: Dict = item[1]  # note that item[0] is the 🔑 cardName

		# sometimes the data won't exist because sample size was too small
		if dataSetID not in data['filteredStats']:
			return float('-inf')
		else:
			value = data['filteredStats'][dataSetID][stat]
			if value is None:
				return float('-inf')
			return value

	# to obtain stats for a colorPair, we query data['filteredStats'][dataSet],
	# where dataSet ⊂ {default, WU, UG, WR...}.
	sortingStat: str = 'OH WR'
	sortedData = dict(
		sorted(
			masterData.items(),
			key=lambda item: statSortKey(item, sortingStat),
			reverse=True)
	)

	# sample master.json item:
	'''
	"Glamdring": {
        "Name": "Glamdring",
        "ALSA": 2.1737089201877935,
        "ATA": 2.4025974025974026,
        "URL": "https://cards.scryfall.io/border_crop/...
        "Color": "",
        "Rarity": "M",
        "filteredStats": {
            "all": {
                "GIH WR": 0.6238532110091743,
                "# GIH": 327,
                "OH WR": 0.6060606060606061,
                "# OH": 99,
                "GD WR": 0.631578947368421,
                "# GD": 228,
                "IWD": 0.07212907307813987,
                "z-scores": {
                    "GIH WR": 0.4240168966164874,
                    "OH WR": 0.17294603764905228,
                    "GD WR": 0.39138079897644223,
                    "IWD": 1.0218922920345261
                }
            },
	'''
	# get μ, σ pair to display in header
	gdwrMean: float = statsData[dataSetID]['GD WR']['mean']
	gdwrStdDev: float = statsData[dataSetID]['GD WR']['stdDev']
	ohwrMean: float = statsData[dataSetID]['OH WR']['mean']
	ohwrStdDev: float = statsData[dataSetID]['OH WR']['stdDev']

	# header: display columns and title above the colorPairStrs
	# generally, spaces come after the column
	print(
		f'     n ' 	# GIH: sample size
		f'alsa '
		
		f'| '  
		f'   '    	# ohwrGrade: 2 char + 1 space
		f'      '   # OH z-score: 5 char + 1 space, e.g. '-1.50'
		f'  OH ' 	# ohwr: 4 char + 1 space, e.g. 54.8
		
		f'| '  	
		f'   '  	# gdwrGrade: 2 char + 1 space
		f'      '  	# GD z-score
		f'  GD '  	# gdwr: 4 char + 1 space
		
		f'| '  		
		f'   IWD'   # IWD: 4 char + 1 space, e.g. -15.2pp
		f'   '		# ' ← ' in rows	
		f'{dataSetID} μ={ohwrMean*100:4.1f}, σ={ohwrStdDev*100:3.1f}'
	)


	# display stats of selected cards from fuzzy input matching
	for cardName, cardData in sortedData.items():
		if cardName in cardNameList:
			if dataSetID not in cardData['filteredStats']:
				print(f'🥝 not enough data for {cardName} in {dataSetID}')
			else:
				# print the comparison row
				cardStats: Dict = cardData['filteredStats'][dataSetID]
				gdwr: float = cardStats['GD WR']  	# game drawn win rate
				nGd: int = cardStats['# GD']      	# number of games draw
				zGdwr: float = cardStats['z-scores']['GD WR']
				gdwrGrade: str = getGrade(zGdwr)
				ohwr: float = cardStats['OH WR']    # opening hand win rate
				nOh: float = cardStats['# OH']      # times seen in opening hand
				zOhwr: float = cardStats['z-scores']['OH WR']
				ohwrGrade: str = getGrade(zOhwr)
				iwd: float = cardStats['IWD']	    # improvement when drawn
				alsa: float = cardData['ALSA']		# average last seen at

				# grab the mana cost from our collapsed scryfall dictionary:
				# format is [cardName, mana cost] where latter is formatted
				# 1UUU instead of {1}{U}{U}{U}
				manacost: str = nameManacostDict[cardName]

				print(
					f'{cardStats["# GIH"]:6} '
					f'{alsa:4.1f} '
					f'| '
					f'{ohwrGrade:2} {zOhwr:>5.2f} {ohwr*100:4.1f} '
					f'| '
					f'{gdwrGrade:2} {zGdwr:>5.2f} {gdwr*100:4.1f} '
					f'| '
					f'{iwd*100:4.1f}pp'
					f' ← {cardName}'
				)


# get card data from data/master.json and display it for each cardName in
# cardNameList! The dataSet is parameterized.
def printCardData(
		cardNameList: List[str],
		nameManacostDict,
		dataSetStr: str,
		displayHeaderFlag=True):

	global compareOne
	global displayIwdGrade, displayGihOhDiff, displayOhZscore, \
		displayRarityAndMv

	# open master.json to query for data
	# sample master.json
	# "Birthday Escape": {
	# 	"Name": "Birthday Escape",
	# 	"ALSA": 4.787610685652746,
	# 	"ATA": 6.028844661098519,
	# 	"URL": "https://cards.scryfall.io/border_crop/front/4/2/42db2313-b13d-4292-bef2-bf86f989d32f.jpg?1686169032",
	# 	"Color": "U",
	# 	"Rarity": "C",
	# 	"filteredStats": {
	# 		"default": {
	# 			"GIH WR": 0.5960239727329169,
	# 			"OH WR": 0.5751692517104273,
	# 			"# GIH": 78923,
	# 			"# OH": 27917,
	# 			"IWD": 0.06738294709189119
	# 		},
	# 		"WU": {
	# 			"GIH WR": 0.5773472122024116,
	# 			"OH WR": 0.54628269174258,
	# 			"# GIH": 9703,
	# 			"# OH": 3403,
	# 			"IWD": 0.07841650219385726
	# 		},
	jsonPath: str = f'data/master.json'
	with open(jsonPath, 'r', encoding='utf-8') as jsonFileHandler:
		masterData: Dict = json.load(jsonFileHandler)

	# extra newline if we're comparing multiple cards
	if not compareOne:
		print('')

	def sortingKey(item, stat: str):
		data: Dict = item[1]  # note that item[0] is the 🔑 cardName

		# sometimes the data won't exist because sample size was too small
		if dataSetStr not in data['filteredStats']:
			return float('-inf')
		else:
			value = data['filteredStats'][dataSetStr][stat]
			if value is None:
				return float('-inf')
			return value

	# note that to obtain stats for a colorPair, we query
	# data['filteredStats'][dataSet], where dataSet ⊂ {default, WU, UG, WR...}
	# sort by GIH WR manually in case it's not already sorted that way in csv
	sortingStat: str = 'GIH WR'
	sortedData = dict(
		sorted(
			masterData.items(),
			key=lambda item: sortingKey(item, sortingStat),
			reverse=True)
	)

	# open the statistics data file to query for μ, σ
	jsonPath: str = f'data/statistics.json'
	with open(jsonPath, 'r', encoding='utf-8') as statsFileHandler:
		cardStatistics: Dict = json.load(statsFileHandler)

	# grab the mean and standard deviation from statistics.json:
	#
	#     "WU": {
	#         "GIH WR": {
	#             "mean": 0.5491077666469387,
	#             "stdDev": 0.040215101426471105
	#         },
	#         "OH WR": {
	#             "mean": 0.5209195619740031,
	#             "stdDev": 0.042789373519670264
	#         },
	#         "IWD": {
	#             "mean": 0.061158040767395096,
	#             "stdDev": 0.04112565649327313
	#         }
	#     },
	gihwrMean: float = cardStatistics[dataSetStr]['GIH WR']['mean']
	gihwrStdDev: float = cardStatistics[dataSetStr]['GIH WR']['stdDev']
	ohwrMean: float = cardStatistics[dataSetStr]['OH WR']['mean']
	ohwrStdDev: float = cardStatistics[dataSetStr]['OH WR']['stdDev']

	if displayHeaderFlag:
		displayHeader(dataSetStr, gihwrMean, gihwrStdDev)

	# display stats of selected cards
	for cardName, cardData in sortedData.items():
		# some cards don't have data: check if it's actually in our GIHWR dict
		if cardName in cardNameList:

			# this contains the 5 pieces of data specific to this colorPair
			cardStats: Dict = cardData['filteredStats'][dataSetStr]
			gihwr: float = cardStats['GIH WR']  # game in hand win rate
			nGih: int = cardStats['# GIH']      # number of times seen in hand
			ohwr: float = cardStats['OH WR']    # opening hand win rate
			nOh: float = cardStats['# OH']      # times seen in opening hand
			iwd: float = cardStats['IWD']	    # improvement when drawn

			# note '🔑 color' is not in filteredStats as it applies to the
			# entire card regardless of color archetype
			color: str = cardData['Color']
			rarity: str = cardData['Rarity']

			# initialize strings for grades, e.g. A-, C+, B, S
			gihwrGrade: str = ' '  # empty space for alignment
			ohwrGrade: str = ' '
			iwdGrade: str = ' '

			# only process data if sample size is significant: do the number of
			# games in hand exceed the minimum sample size?
			if nGih > minimumSampleSize:
				# calculate how many stdDevs away from the mean?
				# zscore = (x-μ) / σ
				gihwrZScore: float = (gihwr - gihwrMean) / gihwrStdDev

				# iterate reversed gradeBounds list: ('A+', 2.17) ('B', 0.83)
				# if zScore is greater than current iterated value:
				# 	replace gradeStr with key: 'A+', 'B', etc.

				# TODO encapsulate grade-finding based on parameter: stat
				#   still need to implement iwdGrade and ohwrGrade
				# e.g. GIH WR, OH WR, IWD
				for gradePair in gradeBounds[::-1]:
					if gihwrZScore >= gradePair[1]:
						gihwrGrade = gradePair[0]

				ohwrZScore: float = (ohwr - ohwrMean) / ohwrStdDev
				alsa: float = float(cardData["ALSA"])
				ohwrStr: str = f'{ohwr * 100:4.1f}%' if ohwr else f'    -'

				# display difference in zscore between GIHWR and OHWR
				ogDifStr: str = ''
				if displayGihOhDiff:
					if ohwrZScore:
						ogDif: float = ohwrZScore - gihwrZScore
						ogDifStr = f'{ogDif:5.2f}'
					else:
						ogDifStr = '    -'

				# opening hand win rate z score display
				ohwrZscoreStr: str = ''
				if displayOhZscore:
					if ohwrZScore:
						ohwrZscoreStr = f'{ohwrZScore:5.2f}'

				# grab the mana cost from our collapsed scryfall dictionary:
				# format is [cardName, mana cost] where latter is formatted
				# 1UUU instead of {1}{U}{U}{U}
				manacost: str = nameManacostDict[cardName]

				iwdGradeStr: str = ''
				if displayIwdGrade:
					iwdGradeStr = f'{iwdGrade:2} '

				rarityMvStr: str = ''
				if displayRarityAndMv:
					# 8 spaces needed for rarity and mana cost, +1 space
					# mv must be 6 because 3WUBRG costs
					rarityMvStr = f'{rarity} {manacost:6} '

				iwdStr: str = f'{iwd * 100:.1f}pp'

				# each row
				print(
					f'{gihwrGrade:2} '
					f'{alsa:4.1f} '
					f'{gihwr * 100:4.1f}% '
					f'{gihwrZScore:5.2f} '
					# f'{ohwrZscoreStr} '
					# f'{ohwrStr} '
					f'{ogDifStr} '
					f'{iwdStr:>6} '
					f'{iwdGradeStr}'
					f'← '
					f'{rarityMvStr}'
					f'{cardName}')
			else:
				manacost: str = nameManacostDict[cardName]
				print(
					f'                                 '
					# f'← {rarity} {manacost:5} {cardName}'
					f'← {cardName}'
				)


def getEmptyStatHeader():
	# [ HEADER ]
	# add 3 spaces for iwd grade, e.g. A+, C-
	iwdGradeHeaderStr: str = '   ' if displayIwdGrade else ''

	# 5 characters for zScore diff
	ogDifHeader: str = ' og Δ' if displayGihOhDiff else ''

	# 8 char width and a whitespace
	rarityMvHeader: str = '         ' if displayRarityAndMv else ''

	result: str = (  # metric and how many characters each metric takes, plus spacing
		f'   '  # grade is 2 + 1 space
		f'alsa '  # ALSA 4 chars + 1 whitespace
		f'  gih '  # GIHWR: 6
		f'    z '  # gihwr zscore 5 + 1
		# f' oh-z ' 	# ohwr zscore 5 + 1
		# f'   oh '		# OHWR: 6
		f'{ogDifHeader}'
		f'    iwd '
		f'{iwdGradeHeaderStr}'
		f'{rarityMvHeader}'
		f'  '  # leading spaces for '← '
	)

	return result


# displays the header for the data set, including set name, mean, and stdDev
def displayHeader(dataSet: str, μ: float, σ: float):
	print(
		f'{getEmptyStatHeader()}'
		f'{dataSet} μ:{μ:.3f}, σ:{σ:.3f}'
	)


# generates a dictionary mapping card names to their mana costs in format '2UUU'
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


main()