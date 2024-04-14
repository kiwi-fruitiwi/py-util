import json
from typing import List, Dict
from enum import Enum


# sample size threshold for being included in mean and stdev calculations
# generally if # GIH is 50000, # OH floats around 20000. # GD is 30000
# this makes sense because GIH is OH+GD
minGihSampleSize: int = 300
minOhSampleSize: int = int(minGihSampleSize * 2 / 5)
minGdSampleSize: int = int(minGihSampleSize * 3 / 5)

# used only in dataAggregator.createMasterJson to check {colorPair} #GIH reaches
# a threshold before adding it to *Master.json files. otherwise those files will
# be littered with colorPair data with tiny sample sizes that are irrelevant
# anyway
minJsonInclusionSampleSize: int = 50

colorPairs: List[str] = [
    'WU', 'WB', 'WR', 'WG',
    'UB', 'UR', 'UG',
    'BR', 'BG',
    'RG'
]

# map between set names and additional inclusions, starting from mkm
extraCardsForEachSet: Dict[str, str] = {
    # 40 cards from 'The List', 10 'special guests'
    'mkm': '((set:kld AND cn:235) OR (set:ORI AND cn:176) OR (set:DGM AND cn:34) OR (e:spg cn≥19 cn≤28) OR (e:plst (((cn≥ cn≤) OR cn:"APC-117" OR cn:"MH1-21" OR cn:"DIS-33" OR cn:"XLN-91" OR cn:"C16-47" OR cn:"SOM-96" OR cn:"MH2-191" OR cn:"ISD-183" OR cn:"DKA-143" OR cn:"MRD-99" OR cn:"ELD-107" OR cn:"DKA-4" OR cn:"RTR-140" OR cn:"ONS-89" OR cn:"WAR-54" OR cn:"DOM-130" OR cn:"HOU-149" OR cn:"MBS-10" OR cn:"RAV-277" OR cn:"2X2-17" OR cn:"STX-220" OR cn:"M14-213" OR cn:"KLD-221" OR cn:"ARB-68" OR cn:"JOU-153" OR cn:"RNA-182" OR cn:"C21-19" OR cn:"UMA-138" OR cn:"MH2-46" OR cn:"VOW-207" OR cn:"ONS-272" OR cn:"UMA-247" OR cn:"SOM-98" OR cn:"DDU-50" OR cn:"CLB-85" OR cn:"DIS-173" OR cn:"SOI-262"))))',
    'otj': '(set:big) OR (set:otp) OR (e:spg cn≥29 cn≤38)'
}

# it's possible to leave out start and end date. defaults to entire format!
baseRequestURL: str = \
    "https://www.17lands.com/card_ratings/data" \
    "?expansion=MKM" \
    "&format=PremierDraft" \
    # "&start_date=2023-09-25" # recent data only, typically last 2 weeks

# a map between player caliber set, e.g. 'all', 'top', 'bottom', 'middle', and
# their 17lands json request URLs
caliberRequestMap: Dict = {
    "all": f'{baseRequestURL}',
    "top": f'{baseRequestURL}&user_group=top'
}


# it appears that ANSI sequences always start with \033
# colors always are in this order:
# 	black red green yellow blue magenta cyan white
# bright foreground colors: [30m → [37m
# standard foreground colors: [90m → [97m
# dim foreground colors: [2;30m → [2;37m
# background colors: [40m → [47m
class ANSI(Enum):
    RESET = '\033[0m'  # Reset to default text color
    UNDERLINE = '\033[4m'
    ITALIC = '\033[3m'

    # the default console text output can be considered 'standard white'
    # but the ANSI 'standard white' looks bold
    BLACK = '\033[90m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    DIM_WHITE = '\033[2;37m'


def displayDict(dictionary):
    # display contents of card dictionary neatly
    for key, value in dictionary.items():
        print(f'\n{key} :')
        for innerKey, innerValue in value.items():
            print(f"    {innerKey}: {innerValue}")


def loadJson(filepath: str) -> Dict:
    """
    Load JSON data from a given file path.
    """
    with open(filepath, 'r', encoding='utf-8') as jsonFileHandler:
        return json.load(jsonFileHandler)
