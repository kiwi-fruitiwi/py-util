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
