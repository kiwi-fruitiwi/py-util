# ⚗️ convert json requests from 17lands.com into a simpler json format keyed by
# cardName for compareDraftPicks.py. Default requests from 17L are lists of
# cards, not keyed by anything.


from typing import Dict
from constants import colorPairs  # color pair list: 'WU', 'WR', 'UG', etc.
from constants import caliberRequestMap # top-players and all-players keys
import json


# converts 17L request json into a custom format that resembles 17L csv export
# saves this new json to 📁 data/ltr-converted
def convertJson(jsonInputPath: str, jsonOutputPath: str):
    with open(jsonInputPath, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    # initialize our resulting json file
    cardDict: Dict[str, object] = {}

    # iterate through each card object and create a json object keyed to 'name'
    # note that GIH includes opening hand, whereas GD or 'ever drawn' does not
    for card in json_data:
        name: str = card['name']
        alsa: float = card['avg_seen']
        ata: float = card['avg_pick']
        ohCount: int = card['opening_hand_game_count']
        ohwr: float = card['opening_hand_win_rate']
        gdCount: int = card['drawn_game_count']
        gdwr: float = card['drawn_win_rate']
        gihCount: int = card['ever_drawn_game_count']
        gihwr: float = card['ever_drawn_win_rate']
        iwd: float = card['drawn_improvement_win_rate']
        imgUrl: str = card['url']

        cardDict[name] = {
            'Name': name,    # "name": "Banish from Edoras",
            'ALSA': alsa,    # "avg_seen": 5.210338680926916,
            'ATA': ata,      # "avg_pick": 7.561547479484173,
            '# OH': ohCount, # "opening_hand_game_count": 2203,
            'OH WR': ohwr,   # "opening_hand_win_rate": 0.4925373134328358,
            '# GD': gdCount, # "drawn_win_rate": 0.5757946210268948,
            'GD WR': gdwr,   # "drawn_game_count": 3272,
            '# GIH': gihCount,
            'GIH WR': gihwr, # "drawn_win_rate": 0.46788990825688076,
            'IWD': iwd,      # "drawn_improvement_win_rate": 0.02599067599067600,
            'URL': imgUrl,   # "url": "https://cards.scryfall.io/border_crop/..."
            'Color': card['color'],
            'Rarity': card['rarity'][0].upper()  # CURM
        }

    # dump new json data into a file
    with open(jsonOutputPath, 'w',
              encoding='utf-8') as json_file_handler:
        json_file_handler.write(json.dumps(cardDict, indent=4))

    # displayDict(cardDict)
    print(f'🌊 {jsonInputPath} converted!')
    

def main():
    inputJsonPath: str = f'data/ltr-requests/'
    outputJsonPath: str = f'data/ltr-converted/'

    # data set names are 'all-players' and 'top-players'
    for dataSetName in caliberRequestMap.keys():
        # convert the all-colors 17L json request first
        allColorsInputPath = f'{inputJsonPath}{dataSetName}/all.json'
        allColorsOutputPath = f'{outputJsonPath}{dataSetName}/all.json'
        convertJson(allColorsInputPath, allColorsOutputPath)

        # iterate through colorPairs list to convert all the other 10 files
        # WU.json, UB.json, UG.json, WR.json, etc.
        for colorPair in colorPairs:
            pairInput: str = f'{inputJsonPath}{dataSetName}/{colorPair}.json'
            pairOutput: str = f'{outputJsonPath}{dataSetName}/{colorPair}.json'
            convertJson(pairInput, pairOutput)


main()

'''
sample JSON element from 17L request:
{
	"seen_count": 6171,
	"avg_seen": 5.210338680926916,
	"pick_count": 853,
	"avg_pick": 7.561547479484173,
	"game_count": 373,
	"win_rate": 0.46380697050938335,
	"sideboard_game_count": 60,
	"sideboard_win_rate": 0.36666666666666664,
	"opening_hand_game_count": 67,
	"opening_hand_win_rate": 0.4925373134328358,
	"drawn_game_count": 109,
	"drawn_win_rate": 0.46788990825688076,
	"ever_drawn_game_count": 176,
	"ever_drawn_win_rate": 0.4772727272727273,
	"never_drawn_game_count": 195,
	"never_drawn_win_rate": 0.4512820512820513,
	"drawn_improvement_win_rate": 0.025990675990676004,
	"name": "Banish from Edoras",
	"color": "W",
	"rarity": "common",
	"url": "https://cards.scryfall.io/border_crop/front/a/4/a4410076-e1fe-45f3-a0ca-a91ab0133ff4.jpg?1686397326",
	"url_back": "",
	"types": [
		"Sorcery"
	]
},

this is what the 17L csv download converts to:
"Orcish Bowmasters": {
    "Name": "Orcish Bowmasters",
    "Color": "B",
    "Rarity": "R",
    "# Seen": "632",
    "ALSA": "1.57",
    "# Picked": "484",
    "ATA": "1.54",
    "# GP": "2483",
    "GP WR": "61.7%",
    "# OH": "438",
    "OH WR": "74.0%",
    "# GD": "615",
    "GD WR": "68.6%",
    "# GIH": "1053",
    "GIH WR": "70.8%",
    "# GNS": "1424",
    "GNS WR": "54.8%",
    "IWD": "16.1pp"
}
'''