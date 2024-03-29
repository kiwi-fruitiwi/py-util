import json

from typing import List, Dict
from constants import colorPairs
from constants import ANSI
from constants import minGihSampleSize
from constants import caliberRequestMap

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


gihwrDisplayToggle: bool = True
ohwrDisplayToggle: bool = True
gdwrDisplayToggle: bool = True
iwdDisplayToggle: bool = True

columnMark: str = f'{ANSI.BLACK.value}|{ANSI.RESET.value}'


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



def printColumnHeader(statStr: str):
	print(
		f'{columnMark} '
		f'   '  			# grade
		f'     '  			# z-score
		f' {statStr:>3}'
		f' ', end=''  	# stat name
	)


def printColumnData(statKey: str, data: Dict, colorPair: str):
	"""
	prints a column of data inside various console data displays
	:param statKey: "GIH WR", "OH WR", "GD WR"
	:param data: typically master.json → cardData['filteredStats']
	:param colorPair: "all", "WU", "UG", "BR", etc.
	:return:
	"""
	colorStats: Dict = data[colorPair]
	zScores: Dict = colorStats['z-scores']

	# e.g. 58.2% +1.1 B-
	statPercentage: str = validate(colorStats[statKey], '{:4.1f}', 100)
	statZScore: str = validate(zScores[statKey], '{:>4.1f}')
	statGrade: str = validate(getGrade(zScores[statKey]), '{:2}')

	print(
		f'{columnMark} '
		f'{statGrade} '
		f'{ANSI.DIM_WHITE.value}{statZScore}{ANSI.RESET.value} '
		f'{statPercentage} ', end=''
	)


def printArchetypesData(
		cardName: str,
		masterJson: Dict,
		statsJson: Dict,
		caliber: str,
		optionalDescription: str = ''):
	"""
	output data from archetypes that satisfy the sample size requirement
	:param cardName:
	:param masterJson: a list of card data keyed by name
	:param statsJson: contains μ σ info for stats per color pair
	:param caliber: 'top', 'all' for allPlayers vs topPlayers dataSet
	:param optionalDescription: additional description slot for secretGoldCards
	:return:
	"""

	cardStats: Dict = masterJson[cardName]

	# header: display columns and title above the colorPairStrs
	print(
		f'{ANSI.DIM_WHITE.value}[DATASET] {ANSI.RESET.value}'
		f'{caliber} '
		f'{ANSI.DIM_WHITE.value}players{ANSI.RESET.value}'
	)

	validatedAlsa: str = validate(cardStats['ALSA'], '{:.1f}')
	print(
		f'{ANSI.BLUE.value}{cardName}{ANSI.RESET.value} '
		f'→ ALSA {validatedAlsa} '
		f'{optionalDescription}'
	)

	print(
		f'     n '  # # GIH: sample size
		f'{columnMark} '  # outer column
		f'    '
		f'{columnMark} '
		f'   μ '
		f'{columnMark} '
		f'  σ '
		, end=''   	# colorPair: 2 char + 1 space ← now 3 with 'all' included
	)

	if gihwrDisplayToggle:
		printColumnHeader('GIH')

	if ohwrDisplayToggle:
		printColumnHeader('OH')

	if gdwrDisplayToggle:
		printColumnHeader('GD')

	if iwdDisplayToggle:
		print(
			f'{columnMark}  '  # column break
			f'   '  # iwdGrade: 2 char + 1 space
			f'    '  # IWD z-score
			f'   IWD', end='' # IWD: 4 char + 1 space, e.g. -15.2pp
		)

	print(f'')  # newline

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
			# printCardStatsRow(cardName, masterJson, statsJson, caliber)

			colorStats: Dict = stats[colorPair]
			zScores: Dict = colorStats['z-scores']

			iwd: str = validate(colorStats['IWD'], '{:4.1f}', 100)
			zIwd: str = validate(zScores['IWD'], '{:>4.1f}')
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
			archetypeThreshold: int = 500

			if gihCount > archetypeThreshold:

				# categorize by GIHWR μ σ
				gihwrMean: float = statsJson[colorPair]['GIH WR']['mean']
				gihwrStdev: float = statsJson[colorPair]['GIH WR']['stdev']

				ohwrMeanStr: str = validate(gihwrMean, '{:4.1f}', 100)
				ohwrStdevStr: str = validate(gihwrStdev, '{:3.1f}', 100)


				print(
					f'{ANSI.DIM_WHITE.value}{gihCountStr:>6}{ANSI.RESET.value} '
					f'{columnMark} '					
					f'{ANSI.WHITE.value}{colorPair:>3}{ANSI.RESET.value} '
					f'{columnMark} '
					f'{ANSI.DIM_WHITE.value}{ohwrMeanStr}{ANSI.RESET.value} '
					f'{columnMark} '
					f'{ANSI.DIM_WHITE.value}{ohwrStdevStr}{ANSI.RESET.value} ', end=''
				)

				if gihwrDisplayToggle:
					printColumnData('GIH WR', stats, colorPair)

				if ohwrDisplayToggle:
					printColumnData('OH WR', stats, colorPair)

				if gdwrDisplayToggle:
					printColumnData('GD WR', stats, colorPair)

				if iwdDisplayToggle:
					print(
						f'{columnMark} '					
						f'{iwdGrade} '
						f'{ANSI.DIM_WHITE.value}{zIwd}{ANSI.RESET.value} '
						f'{iwd}{ANSI.DIM_WHITE.value}{iwdSuffix}{ANSI.RESET.value}', end=''
					)

				print(f'')  # newline
	pass


# TODO similar to printCardComparison, but new caliber column, μ σ per entry
# 	and new header → [CARD] {cardName} {rarity} in {colorPair / all}
def printCaliberDifferences(
		cardName: str,
		dataSetID: str, # colorPair / all
		topMaster: Dict, topStats: Dict,
		allMaster: Dict, allStats: Dict):

	calibers: List[str] = list(caliberRequestMap.keys())
	statsDict: Dict[str, Dict[str, float]] = {}

	# each row will need μ, σ data
	topOhwrMean: float = topStats[dataSetID]['OH WR']['mean']
	topOhwrStdev: float = topStats[dataSetID]['OH WR']['stdev']
	allOhwrMean: float = allStats[dataSetID]['OH WR']['mean']
	allOhwrStdev: float = allStats[dataSetID]['OH WR']['stdev']

	statsDict.update({'top': {'mean': topOhwrMean, 'stdev': topOhwrStdev}})
	statsDict.update({'all': {'mean': allOhwrMean, 'stdev': allOhwrStdev}})

	# find difference in GIH WR z-scores between calibers to display in title
	topGihz: float = topMaster[cardName]['filteredStats'][dataSetID]['z-scores']['GIH WR']
	allGihz: float = allMaster[cardName]['filteredStats'][dataSetID]['z-scores']['GIH WR']
	signMarker: str = ''

	if topGihz and allGihz:
		difference: float = (topGihz - allGihz)
		diffStr: str = f'{difference:>5.2f}'

		if topGihz - allGihz > 0:
			signMarker = f'📈'
		else:
			signMarker = f'📉'
			return

	# display title with ANSI coloring:
	# 	[CARD] {rarity} {cardName} in {colorPair / all}
	rarity: str = styleRarity(allMaster[cardName]["Rarity"])
	print(
		f'{diffStr} {signMarker} '
		# f'{ANSI.DIM_WHITE.value}[CARD]{ANSI.RESET.value} '
		f'{rarity} '
		f'{ANSI.BLUE.value}{cardName}{ANSI.RESET.value} '
		f'{ANSI.DIM_WHITE.value}in{ANSI.RESET.value} '
		f'{ANSI.WHITE.value}{dataSetID}{ANSI.RESET.value}'
	)


	# header: display column titles
	print(
		f'caliber '
		f'     n '  # GIH: sample size
		f'alsa ', end='')

	if gihwrDisplayToggle:
		printColumnHeader('GIH')

	if ohwrDisplayToggle:
		printColumnHeader('OH')

	if gdwrDisplayToggle:
		printColumnHeader('GD')

	print(
		f'{columnMark} '
		f'   IWD')  	# IWD: 4 char + 1 space, e.g. -15.2pp

	# print data per row for each caliber, currently only top and all players:
	# all
	print('    all ', end='')
	printCardStatsRow(
		cardName, allMaster, allStats, dataSetID,
		displayMvName=False,
		displayArchetypeStats=True
	)


	print('    top ', end='')
	printCardStatsRow(
		cardName, topMaster, topStats, dataSetID,
		displayMvName=False,
		displayArchetypeStats=True
	)

	# newline
	print(f'')

# top


# displays a partial line of card stats
def printCardStatsRow(
		cardName, masterJson: Dict, statsJson: Dict, dataSetID,
		displayMvName: bool = True,
		displayArchetypeStats: bool = False):

	cardData = masterJson[cardName]
	stats: Dict = cardData['filteredStats']

	# make sure data is available and we meet sample size requirements
	if dataSetID not in cardData['filteredStats']:
		print(f'🥝 not enough data for {cardName} in {dataSetID}')
	elif cardData['filteredStats'][dataSetID]['# GIH'] <= minGihSampleSize:
		print(
			f'🌊 not enough data for {cardName} in {dataSetID}: <{minGihSampleSize}')
	else:
		cardStats: Dict = stats[dataSetID]
		iwd: str = validate(cardStats['IWD'], '{:4.1f}', 100)
		iwdFoundFlag: bool = (iwd != '{:4}'.format(' '))
		iwdSuffix: str = 'pp' if iwdFoundFlag else '  '

		# average last seen at
		alsa: str = validate(cardData['ALSA'], '{:4.1f}')

		# dim 'C' in rarity
		rarity: str = styleRarity(cardData["Rarity"])

		manaCost: str = cardData["manaCost"]

		print(
			f'{ANSI.DIM_WHITE.value}{cardStats["# GIH"]:6}{ANSI.RESET.value} '
			f'{alsa} ', end=''
		)

		# display data from colorPairs in cardData['filteredStats']
		if gihwrDisplayToggle:
			printColumnData('GIH WR', stats, dataSetID)

		if ohwrDisplayToggle:
			printColumnData('OH WR', stats, dataSetID)

		if gdwrDisplayToggle:
			printColumnData('GD WR', stats, dataSetID)

		print(
			f'{columnMark} '
			f'{iwd}{ANSI.DIM_WHITE.value}{iwdSuffix}{ANSI.RESET.value} ',
			end='')

		if displayMvName:
			print(
				f'{rarity} '
				f'{manaCost:>4} '
				f'← {ANSI.BLUE.value}{cardName}{ANSI.RESET.value}'
			)
		elif displayArchetypeStats:
			# categorize by GIHWR μ σ
			gihwrMean: float = statsJson[dataSetID]['GIH WR']['mean']
			gihwrStdev: float = statsJson[dataSetID]['GIH WR']['stdev']

			ohwrMeanStr: str = validate(gihwrMean, '{:4.1f}', 100)
			ohwrStdevStr: str = validate(gihwrStdev, '{:3.1f}', 100)

			print(
				f' '  # ' ← ' in rows    
				f'{ANSI.WHITE.value}{dataSetID}{ANSI.RESET.value} '
				f'{ANSI.DIM_WHITE.value}μ={ANSI.RESET.value}{ohwrMeanStr}, '
				f'{ANSI.DIM_WHITE.value}σ={ANSI.RESET.value}{ohwrStdevStr}'
			)
		else: # restore the newline
			print(f'')


def printCardComparison(cardNameList: List[str], dataSetID: str, caliber: str):
	"""
	prints data from many cards at once
	:param cardNameList: fuzzy input matching results
	:param dataSetID: 'all', 'WU', 'UG', 'RG'
	:param caliber: descriptor for 'all' vs 'top' player data
	:return:
	"""

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
	sortingStat: str = 'GIH WR'
	sortedData = dict(
		sorted(
			masterData.items(),
			key=lambda item: statSortKey(item, sortingStat),
			reverse=True)
	)

	# get μ, σ pair to display in header
	gihwrMean: float = statsData[dataSetID]['GIH WR']['mean']
	gihwrStdev: float = statsData[dataSetID]['GIH WR']['stdev']

	# header: display columns and title above the colorPairStrs
	# generally, spaces come after the column
	print(
		f'{ANSI.DIM_WHITE.value}[DATASET]: {ANSI.RESET.value}'
		f'{caliber} '
		f'{ANSI.DIM_WHITE.value}players{ANSI.RESET.value}'
		f'\n'
		f'     n '  # GIH: sample size
		f'alsa ', end='')

	if gihwrDisplayToggle:
		printColumnHeader('GIH')

	if ohwrDisplayToggle:
		printColumnHeader('OH')

	if gdwrDisplayToggle:
		printColumnHeader('GD')

	ohwrMeanStr: str = validate(gihwrMean, '{:4.1f}', 100)
	ohwrStdevStr: str = validate(gihwrStdev, '{:3.1f}', 100)

	print(
		f'{columnMark} '
		f'   IWD'  	# IWD: 4 char + 1 space, e.g. -15.2pp
		f' R'
		f'     ' 	# mana cost
		f'   '  	# ' ← ' in rows	
		f'{ANSI.WHITE.value}{dataSetID}{ANSI.RESET.value} '
		f'{ANSI.DIM_WHITE.value}μ={ANSI.RESET.value}{ohwrMeanStr}, '
		f'{ANSI.DIM_WHITE.value}σ={ANSI.RESET.value}{ohwrStdevStr}'
	)

	# display stats of selected cards from fuzzy input matching
	for cardName, cardData in sortedData.items():
		if cardName in cardNameList:
			printCardStatsRow(cardName, masterData, statsData, dataSetID)


def styleRarity(rarity: str):
	match rarity:
		case 'C': return f'{ANSI.DIM_WHITE.value}{rarity}{ANSI.RESET.value}'
		case 'R': return f'{ANSI.WHITE.value}{rarity}{ANSI.RESET.value}'
		case 'M': return f'{ANSI.WHITE.value}{rarity}{ANSI.RESET.value}'
		case _: return rarity
