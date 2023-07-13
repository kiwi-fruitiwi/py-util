import Levenshtein  # makes finding the L-distance between strings much faster
import json

from fuzzywuzzy import process
from typing import List, Dict
from scryfallCardFetch import printCardText
from constants import colorPairs
from cardDisplay import printCardComparison, printArchetypesData


displayCardFetchList: bool = False
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

	global displayCardFetchList
	done: bool = False

	while not done:
		printFlag = False
		userInput: str = input('\nEnter cards: ')

		# split the input string into a list using ',' as delimiter
		inputCardNames: List[str] = userInput.split(',')

		# trim leading and trailing whitespace
		strippedCardNames: List[str] = [name.strip() for name in inputCardNames]


		# special command: print card text if first char is '!'
		# we ignore all but the first token in the input string this way
		firstElement: str = strippedCardNames[0]
		if firstElement[0] == '!':
			cardName: str = firstElement[1:].strip()  # remove '!' and spaces
			bestMatch = process.extractOne(cardName, masterJson.keys())

			# process always returns a list even if its length is 1
			printCardText(bestMatch[0], scryfallJson)

			# stop here! no need to print data if we're just checking oracleText
			continue


		# dataset we'll be loading from json. default is 'all'
		dataSetID: str = f'all'

		# special command: colorPair with colon, e.g. 'WU: '
		# check if first element contains ':'. use this to determine what
		# 	this will open data from the corresponding file and cache it
		# strip after in case there are multiple spaces after 'WU:'
		if ':' in firstElement:
			tokens: List[str] = firstElement.split(':')

			# there should be only two tokens: colorPair: cardName
			# and colorPair must be in [WU, WB, WR, WG, etc.]
			assert len(tokens) == 2
			assert tokens[0].upper() in colorPairs

			# save what our current data set is so it's visible in the output
			dataSetID = tokens[0].upper().strip()
			strippedCardNames[0] = tokens[1].strip()

		# set up list of card names matched to our input
		cardFetchList: List[str] = []

		for name in strippedCardNames:
			# extractOne returns a tuple like this: ('Arwen Undómiel', 90)
			# we're just interested in the name, not the closeness
			bestMatch = process.extractOne(name, masterJson.keys())

			if bestMatch:
				bestMatchName = bestMatch[0]  # process always returns a List
				cardFetchList.append(bestMatchName)
			else:
				print(f'🍆 best match not found for {name}')

		# if there's only one card, we will show an archetype analysis!
		if len(cardFetchList) == 1:
			cardName: str = cardFetchList[0]
			printArchetypesData(cardName, masterJson[cardName])
		else:
			# print a list of names if we're matching more than one card
			if displayCardFetchList:
				[print(name) for name in cardFetchList]
			printCardComparison(cardFetchList, dataSetID)

		# if there's only one card name input and it's preceded by '!'
		# → print the card's spoiler text
		# recall that printFlag is set when user input is prefixed with '!'
		if printFlag and len(cardFetchList) == 1:
			printCardText(cardFetchList[0], scryfallJson)


main()