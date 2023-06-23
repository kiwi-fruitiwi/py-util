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

# it's possible to leave out start and end date. defaults to entire format?
url = 'https://www.17lands.com/card_ratings/data?expansion=LTR&' \
	  'format=PremierDraft&start_date=2023-06-20&end_date=2023-06-21'

response = requests.get(url)
data = response.json()

# open a json file handler and use json.dumps method to dump data
with open('custom17Lrequest.json', 'w', encoding='utf-8') as json_file_handler:
	json_file_handler.write(json.dumps(data, indent=4))

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