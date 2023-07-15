import json

from typing import List, Dict
from constants import colorPairs

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
		f'     n '  # # GIH: sample size
		f'| '  # outer column
		f'   '  # colorPair: 2 char + 1 space
		f'|  '  # ' → '
		f'   '  # ohwrGrade: 2 char + 1 space
		f'    '  # OH z-score: 5 char + 1 space, e.g. '-1.50'
		f'   OH'  # ohwr: 4 char + 1 space, e.g. 54.8
		f' |  '  # column break
		f'   '  # gdwrGrade: 2 char + 1 space
		f'    '  # GD z-score
		f'   GD'  # gdwr: 4 char + 1 space
		f' |  '  # column break
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
				f'{ohwrGrade:2} {zOhwr:>5.2f} {ohwr * 100:4.1f}'
				f' | '
				f'{gdwrGrade:2} {zGdwr:>5.2f} {gdwr * 100:4.1f}'
				f' | '
				f'{iwdGrade:2} {zIwd:>5.2f} {iwd * 100:4.1f}pp'
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
		f'\n'
		f'     n '  # GIH: sample size
		f'alsa '

		f'| '
		f'   '  # ohwrGrade: 2 char + 1 space
		f'      '  # OH z-score: 5 char + 1 space, e.g. '-1.50'
		f'  OH '  # ohwr: 4 char + 1 space, e.g. 54.8

		f'| '
		f'   '  # gdwrGrade: 2 char + 1 space
		f'      '  # GD z-score
		f'  GD '  # gdwr: 4 char + 1 space

		f'| '
		f'   IWD'  # IWD: 4 char + 1 space, e.g. -15.2pp
		f' R'
		f'   '  # ' ← ' in rows	
		f'{dataSetID} μ={ohwrMean * 100:4.1f}, σ={ohwrStdDev * 100:3.1f}'
	)

	# display stats of selected cards from fuzzy input matching
	for cardName, cardData in sortedData.items():
		if cardName in cardNameList:
			if dataSetID not in cardData['filteredStats']:
				print(f'🥝 not enough data for {cardName} in {dataSetID}')
			else:
				# print the comparison row
				cardStats: Dict = cardData['filteredStats'][dataSetID]
				gdwr: float = cardStats['GD WR']  # game drawn win rate
				nGd: int = cardStats['# GD']  # number of games draw
				zGdwr: float = cardStats['z-scores']['GD WR']
				gdwrGrade: str = getGrade(zGdwr)
				ohwr: float = cardStats['OH WR']  # opening hand win rate
				nOh: float = cardStats['# OH']  # times seen in opening hand
				zOhwr: float = cardStats['z-scores']['OH WR']
				ohwrGrade: str = getGrade(zOhwr)
				iwd: float = cardStats['IWD']  # improvement when drawn
				alsa: float = cardData['ALSA']  # average last seen at
				rarity: str = cardData["Rarity"]

				print(
					f'{cardStats["# GIH"]:6} '
					f'{alsa:4.1f} '
					f'| '
					f'{ohwrGrade:2} {zOhwr:>5.2f} {ohwr * 100:4.1f} '
					f'| '
					f'{gdwrGrade:2} {zGdwr:>5.2f} {gdwr * 100:4.1f} '
					f'| '
					f'{iwd * 100:4.1f}pp '
					f'{rarity} '
					f'← {cardName}'
				)