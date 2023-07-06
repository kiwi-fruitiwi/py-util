# ☒ read 📁 data/ltr-auto/all.json
# ☒ iterate through entries, printing each name and final count
# identify stats we need and what format we want:
#   # Seen
#   ATA
#   GP WR
#   OH WR
#   GIH WR
#   IWD
# ask GPT how to create this custom json
# print
# write to file
# have compareDraftPicks read from this file instead! 📁 converted-ratings-all.json
#   in the future, make converted-ratings-{colorPairStr}.json
#   read those when queries are prefaced with 'WU: ' or 'UR: '


from typing import List, Dict
import json

cardDict: Dict[str, object] = {}

with open('data/ltr-auto/all.json', 'r', encoding='utf-8') as json_file_handler:
    json_data = json.load(json_file_handler)

    # iterate through each card object and create a json object keyed to 'name'
    for card in json_data:
        # name, ALSA, ATA, GIH WR, OH WR, IWD
        name: str = card['name']
        alsa: float = card['avg_seen']
        ata: float = card['avg_pick']
        ohwr: float = card['opening_hand_win_rate']

        cardDict[name] = {
            'Name': name,   # "name": "Banish from Edoras",
            'ALSA': alsa,   # "avg_seen": 5.210338680926916,
            'ATA': ata,     # "avg_pick": 7.561547479484173,
            'OH WR': ohwr,  # "opening_hand_win_rate": 0.4925373134328358,
        }

    # print(f'🥝 {cardDict}')

    # display contents of card dictionary neatly
    for card in cardDict:
        print(f'{card}')

    for key, value in cardDict.items():
        print(f'\n{key} :')
        for innerKey, innerValue in value.items():
            print(f"    {innerKey}: {innerValue}")


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