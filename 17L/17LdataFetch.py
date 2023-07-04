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
