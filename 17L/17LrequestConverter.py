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


with open('data/ltr-auto/all.json', 'r', encoding='utf-8') as json_file_handler:
    json_data = json.load(json_file_handler)

    cardCount: int = 0
    for card in json_data:
        name = card['name']
        print(name)
        cardCount += 1

    print(f'🐳: {cardCount}')