import requests
import json

url = 'https://www.17lands.com/card_ratings/data?' \
	  'expansion=LTR' \
	  '&format=PremierDraft' \
	  #'&colors=WU'

response = requests.get(url)
data = response.json()

print(json.dumps(data, indent=3))