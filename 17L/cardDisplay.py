import json

from typing import List, Dict
from constants import colorPairs
from constants import ANSI
from constants import minGihSampleSize

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


def getGrade(zScore: float):
	"""
	convert a z-score into a grade based on gradeBounds mapping
	:param zScore:
	:return: e.g. 'A-', 'B', 'D+', 'F'
	"""
	if zScore is None:
		return None

	letterGrade: str = ''

	# iterate reversed gradeBounds list: ('A+', 2.17) ('B', 0.83)
	# if zScore is greater than current iterated value:
	# 	replace gradeStr with key: 'A+', 'B', etc.
	for gradePair in gradeBounds[::-1]:
		if zScore >= gradePair[1]:
			letterGrade = gradePair[0]
	return letterGrade


def validate(value: float | None, validFormat: str, scale: int = 1) -> str:
	"""
	helper method to validate values, e.g. colorStats['z-scores']['OH WR']
	returns the appropriate whitespace if 'None' is encountered, but formats
	properly according to supplied formatStrings if value exists

	makes sure our output does not break when we encounter null values in json
	:param value: dictionary value that can be a float or 'None'
	:param validFormat: an f-string format, e.g. {:4.1f}, {:>5.2f}, {:2}
	:param scale: sometimes we want to multiply the value by 100, e.g. 0.55 to
		55 to indicate a percentage
	:return: a formatted string with specified spacing
	"""
	# the format for 'None' will always be just the spacing from validFormat
	# {:>5.2f} → {:>5}
	# {:4.1f} → {:4}
	if '.' in validFormat:
		noneFormat: str = validFormat.split('.')[0] + '}'
	else:
		noneFormat: str = validFormat

	if value is None:
		return noneFormat.format(' ')
	else:
		return validFormat.format(value*scale)


def printArchetypesData(cardName: str, cardStats: Dict, caliber: str):
	"""
	output data from archetypes that satisfy the sample size requirement
	:param cardName:
	:param cardStats: json containing data for a single card
	:param caliber: 'top', 'all' for allPlayers vs topPlayers dataSet
	:return:
	"""

	columnMark: str = f'{ANSI.BLACK.value}|{ANSI.RESET.value}'

	# header: display columns and title above the colorPairStrs
	print(
		f'{ANSI.DIM_WHITE.value}[DATASET] {ANSI.RESET.value}'
		f'{caliber} '
		f'{ANSI.DIM_WHITE.value}players{ANSI.RESET.value}'
	)
	print(f'{ANSI.BLUE.value}{cardName}{ANSI.RESET.value} → ALSA {cardStats["ALSA"]:.1f}')
	print(
		f'     n '  # # GIH: sample size
		f'{columnMark} '  # outer column
		f'   '  # colorPair: 2 char + 1 space
		f'{columnMark}  '  # ' → '
		f'   '  # ohwrGrade: 2 char + 1 space
		f'    '  # OH z-score: 5 char + 1 space, e.g. '-1.50'
		f'   OH'  # ohwr: 4 char + 1 space, e.g. 54.8
		f' {columnMark}  '  # column break
		f'   '  # gdwrGrade: 2 char + 1 space
		f'    '  # GD z-score
		f'   GD'  # gdwr: 4 char + 1 space
		f' {columnMark}  '  # column break
		f'   '  # iwdGrade: 2 char + 1 space
		f'    '  # IWD z-score
		f'    IWD'  # IWD: 4 char + 1 space, e.g. -15.2pp
	)

	# iterate through colorPairs data to display the following stats:
	# OH WR, OH WR z-score
	# GD WR, GD WR z-score
	# IWD
	# include the colorPairStr
	# ✒️ ALSA likely not necessary
	stats: Dict = cardStats['filteredStats']

	colorPairsInclAll: list[str] = colorPairs.copy()
	colorPairsInclAll.append('all')
	for colorPair in colorPairsInclAll:

		# output the data we want for each colorPair
		if colorPair in stats:
			colorStats: Dict = stats[colorPair]
			zScores: Dict = colorStats['z-scores']

			ohwr: str = validate(colorStats['OH WR'], '{:4.1f}', 100)
			zOhwr: str = validate(zScores['OH WR'],  '{:>5.2f}')
			ohwrGrade: str = validate(getGrade(zScores['OH WR']), '{:2}')

			gdwr: str = validate(colorStats['GD WR'], '{:4.1f}', 100)
			zGdwr: str = validate(zScores['GD WR'], '{:>5.2f}')
			gdwrGrade: str = validate(getGrade(zScores['GD WR']), '{:2}')

			iwd: str = validate(colorStats['IWD'], '{:4.1f}', 100)
			zIwd: str = validate(zScores['IWD'], '{:>5.2f}')
			iwdGrade: str = validate(getGrade(zScores['IWD']), '{:2}')

			# set a flag if IWD returns an actual value other than 'None'
			iwdFoundFlag: bool = (iwd != '{:4}'.format(' '))

			# remove the 'pp' suffix for IWD if IWD returned 'None'
			iwdSuffix: str = 'pp' if iwdFoundFlag else '  '

			gihCount: int = colorStats["# GIH"]
			gihCountStr: str = f'{gihCount}'

			# if #gih surpasses this, print the archetype data
			# otherwise as of 2023.Sept, 17L no longer publishes request data
			# at low sample size and the lines will show up empty
			archetypeThreshold: int = 750

			if gihCount > archetypeThreshold:
				print(
					f'{ANSI.DIM_WHITE.value}{gihCountStr:>6}{ANSI.RESET.value} '
					f'{columnMark} '
					
					f'{colorPair} {columnMark} '
					f'{ohwrGrade} '
					f'{ANSI.DIM_WHITE.value}{zOhwr}{ANSI.RESET.value} '
					f'{ohwr}'
					f' {columnMark} '
					
					f'{gdwrGrade} '
					f'{ANSI.DIM_WHITE.value}{zGdwr}{ANSI.RESET.value} '
					f'{gdwr}'
					f' {columnMark} '
					
					f'{iwdGrade} '
					f'{ANSI.DIM_WHITE.value}{zIwd}{ANSI.RESET.value} '
					f'{iwd}{ANSI.DIM_WHITE.value}{iwdSuffix}{ANSI.RESET.value}'
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
		cardNameList: List[str],  	# fuzzy input matching results
		dataSetID: str,  			# 'all', 'WU', 'UG', 'RG'
		caliber: str, 				# descriptor for 'all' vs 'top' player data
):

	masterJsonPath: str = f'data/{caliber}Master.json' 	# 'data/allMaster.json'
	statsJsonPath: str = f'data/{caliber}Stats.json' 	# 'data/allStats.json'


	# load aggregated master data
	with open(masterJsonPath) as file:
		masterData: Dict = json.load(file)
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
	with open(statsJsonPath, 'r', encoding='utf-8') as statsFileHandler:
		statsData: Dict = json.load(statsFileHandler)
		'''
		statistics data
	
		"WU": {
			"GIH WR": {
				"mean": 0.5481773664431846,
				"stdev": 0.0396680728733385
			},
			"OH WR": {
				"mean": 0.5200756145211735,
				"stdev": 0.04154648783076403
			},
			"GD WR": {
				"mean": 0.56087617869494,
				"stdev": 0.0389425738105168
			},
			"IWD": {
				"mean": 0.06100664189146016,
				"stdev": 0.04077503221641616
			}
		},
		'''

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

	# get μ, σ pair to display in header
	ohwrMean: float = statsData[dataSetID]['OH WR']['mean']
	ohwrStdev: float = statsData[dataSetID]['OH WR']['stdev']

	columnMark: str = f'{ANSI.BLACK.value}|{ANSI.RESET.value}'

	# header: display columns and title above the colorPairStrs
	# generally, spaces come after the column
	print(
		f'{ANSI.DIM_WHITE.value}[DATASET]: {ANSI.RESET.value}'
		f'{caliber} '
		f'{ANSI.DIM_WHITE.value}players{ANSI.RESET.value}'
		f'\n'
		f'     n '  # GIH: sample size
		f'alsa '

		f'{columnMark} '
		f'   '  	# ohwrGrade: 2 char + 1 space
		f'      '  	# OH z-score: 5 char + 1 space, e.g. '-1.50'
		f'  OH '  	# ohwr: 4 char + 1 space, e.g. 54.8

		f'{columnMark} '
		f'   '  	# gihwr grade
		f'      '  	# z-score
		f' GIH '  	# gihwr

		f'{columnMark} '
		f'   '  # gdwrGrade: 2 char + 1 space
		f'      '  # GD z-score
		f'  GD '  # gdwr: 4 char + 1 space

		f'{columnMark} '
		f'   IWD'  # IWD: 4 char + 1 space, e.g. -15.2pp
		f' R'
		f'   '  # ' ← ' in rows	
		f'{ANSI.WHITE.value}{dataSetID}{ANSI.RESET.value} '
		f'{ANSI.DIM_WHITE.value}μ={ANSI.RESET.value}{ohwrMean * 100:4.1f}, '
		f'{ANSI.DIM_WHITE.value}σ={ANSI.RESET.value}{ohwrStdev * 100:3.1f}'
	)

	# display stats of selected cards from fuzzy input matching
	for cardName, cardData in sortedData.items():
		if cardName in cardNameList:
			if dataSetID not in cardData['filteredStats']:
				print(f'🥝 not enough data for {cardName} in {dataSetID}')
			elif cardData['filteredStats'][dataSetID]['# GIH'] <= minGihSampleSize:
				print(f'🌊 not enough data for {cardName} in {dataSetID}: <{minGihSampleSize}')
			else:
				# print the comparison row
				cardStats: Dict = cardData['filteredStats'][dataSetID]
				zScores = cardStats['z-scores']

				gihwr: str = validate(cardStats['GIH WR'], '{:4.1f}', 100)
				zGihwr: str = validate(zScores['GIH WR'], '{:>5.2f}')
				gihwrGrade: str = validate(getGrade(zScores['GIH WR']), '{:2}')

				gdwr: str = validate(cardStats['GD WR'], '{:4.1f}', 100)
				zGdwr: str = validate(zScores['GD WR'], '{:>5.2f}')
				gdwrGrade: str = validate(getGrade(zScores['GD WR']), '{:2}')

				ohwr: str = validate(cardStats['OH WR'], '{:4.1f}', 100)
				zOhwr: str = validate(zScores['OH WR'],  '{:>5.2f}')
				ohwrGrade: str = validate(getGrade(zScores['OH WR']), '{:2}')

				# improvement when drawn
				# set a flag if IWD returns an actual value other than 'None'
				# remove the 'pp' suffix for IWD if IWD returned 'None'
				iwd: str = validate(cardStats['IWD'], '{:4.1f}', 100)
				iwdFoundFlag: bool = (iwd != '{:4}'.format(' '))
				iwdSuffix: str = 'pp' if iwdFoundFlag else '  '

				# average last seen at
				alsa: str = validate(cardData['ALSA'], '{:4.1f}')
				rarity: str = cardData["Rarity"]

				print(
					f'{ANSI.DIM_WHITE.value}{cardStats["# GIH"]:6}{ANSI.RESET.value} '
					f'{alsa} '
					f'{columnMark} '
					
					f'{ohwrGrade} '
					f'{ANSI.DIM_WHITE.value}{zOhwr}{ANSI.RESET.value} '
					f'{ohwr} '
					f'{columnMark} '
					
					f'{gihwrGrade} '
					f'{ANSI.DIM_WHITE.value}{zGihwr}{ANSI.RESET.value} '
					f'{gihwr} '
					f'{columnMark} '
					
					f'{gdwrGrade} '
					f'{ANSI.DIM_WHITE.value}{zGdwr}{ANSI.RESET.value} '
					f'{gdwr} '
					f'{columnMark} '
					
					f'{iwd}{ANSI.DIM_WHITE.value}{iwdSuffix}{ANSI.RESET.value} '
					f'{rarity} '
					f'← {ANSI.BLUE.value}{cardName}{ANSI.RESET.value}'
				)