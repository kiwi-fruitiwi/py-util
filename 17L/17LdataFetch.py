"""
fetch JSON data from 17L users and color filters
example request uses this URL:
	https://www.17lands.com/card_ratings/data?
		expansion=LTR
		&format=PremierDraft
		&start_date=2023-06-20
		&end_date=2023-06-21
		&colors=WU
		&user_group=top
"""
import requests
import json
from typing import List

# it's possible to leave out start and end date. defaults to entire format!
defaultUrl: str = 'https://www.17lands.com/card_ratings/data?' \
	  'expansion=LTR' \
	  '&format=PremierDraft'

# url for request to which we append '&colors=' and one of the 10 color pairs
colorUrl: str = defaultUrl + '&colors='

colorPairs: List[str] = [
	'WU', 'WB', 'WR', 'WG',
	'UB', 'UR', 'UG',
	'BR', 'BG',
	'RG'
]

# iterate through colorPairs, making a request for each pair
# then dump into 📂ltr-auto as 'allColors.json' or the colorPair name

# first, the 'all.json' output
allColors = requests.get(defaultUrl).json()
with open('data/ltr-auto/all.json', 'w', encoding='utf-8') as json_file_handler:
	json_file_handler.write(json.dumps(allColors, indent=4))

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
'''