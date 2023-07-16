from typing import List, Dict
from enum import Enum


minimumSampleSize: int = 250
minOffColorSampleSize: int = 100

colorPairs: List[str] = [
    'WU', 'WB', 'WR', 'WG',
    'UB', 'UR', 'UG',
    'BR', 'BG',
    'RG'
]

# it's possible to leave out start and end date. defaults to entire format!
baseRequestURL: str = \
    "https://www.17lands.com/card_ratings/data" \
    "?expansion=LTR" \
    "&format=PremierDraft"


# a map between player caliber set, e.g. 'all', 'top', 'bottom', 'middle', and
# their 17lands json request URLs
caliberRequestMap: Dict = {
    "all": f'{baseRequestURL}',
    "top": f'{baseRequestURL}&user_group=top'
}



def displayDict(dictionary):
    # display contents of card dictionary neatly
    for key, value in dictionary.items():
        print(f'\n{key} :')
        for innerKey, innerValue in value.items():
            print(f"    {innerKey}: {innerValue}")