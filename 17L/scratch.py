# scratch file for making small computations
# 1. average ALSA

import json
import statistics
from typing import Dict, List
from datetime import datetime, timedelta


def twoWeeksPrior():
	"""
	output a string in the format '2024-03-02' that's exactly 2 weeks before
	the current date
	"""

	# grab the current date. note datetime.today() gives the date, but now()
	# also adds the time. datetime.today() equivalent to datetime.now().date()
	currentDate = datetime.now()

	# Calculate the date exactly 2 weeks before the current date
	twoWeeksBefore = currentDate - timedelta(days=15)

	# Format the date to match the specified format "YYYY-MM-DD"
	formattedDate = twoWeeksBefore.strftime("%Y-%m-%d")
	return formattedDate


twoWeeksPrior()


# find cards with the highest ratio of:
# 1. GDWR and OHWR z-scores, to
# 2. ATA z-score?
# the goal is to find severely under-drafted cards in the current meta: deceive
# TODO figure out how to address the ATA z-score being negative means it's a
# 	high pick :P
def computeAvgAlsa():
	currentJsonPath: str = f'data/master.json'
	with open(currentJsonPath, 'r', encoding='utf-8') as jsonFileHandler:
		master: Dict = json.load(jsonFileHandler)

	alsaList: List[float] = []
	ataList: List[float] = []
	for cardName, cardData in master.items():
		alsa: float = cardData['ALSA']
		ata: float = cardData['ATA']

		alsaList.append(alsa)
		ataList.append(ata)

	print(f'🐳 average ALSA: {statistics.mean(alsaList)}, σ={statistics.stdev(alsaList)}')

	ata_μ: float = statistics.mean(ataList)
	ata_σ: float = statistics.stdev(ataList)
	print(f'🐳 average ATA: {ata_μ}, σ={ata_σ}')


	# display z-scores for ATA
	for cardName, cardData in master.items():
		ata: float = cardData['ATA']
		ata_z: float = (ata - ata_μ) / ata_σ
		ohwr_z: float = cardData["filteredStats"]["all"]["z-scores"]["OH WR"]

		if ohwr_z:
			print(f'{ata_z:5.2f} 💦 {ohwr_z:5.2f} ← {cardName:16}')

	# eventually sort this and see!


def ansiExperiments():
	# it appears that ANSI sequences always start with \033
	# colors always are in this order:
	# 	black red green yellow blue magenta cyan white
	# bright foreground colors: [30m → [37m
	# standard foreground colors: [90m → [97m
	# dim foreground colors: [2;30m → [2;37m
	# background colors: [40m → [47m

	RESET = '\033[0m'  # Reset to default text color
	PURPLE = '\033[95m'
	CYAN = '\033[96m'
	DARKCYAN = '\033[36m'
	BLUE = '\033[94m'
	BLUE_2 = '\033[34m'
	GREEN = '\033[92m'
	YELLOW = '\033[93m'
	RED = '\033[91m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'
	ITALIC = '\033[3m'

	BRIGHT_WHITE = '\033[37m'
	STANDARD_WHITE = '\033[97m'
	DIM_WHITE = '\033[2;37m'

	print(
		f'This is {BOLD}bolded{RESET} {UNDERLINE}underlined{RESET} '
		f'{ITALIC}italicized{RESET} {BLUE}blue{RESET} {BLUE_2}blue_2{RESET} text'
	)

	print(
		f'{BRIGHT_WHITE}bright{RESET} '
		f'{STANDARD_WHITE}standard{RESET} '
		f'{DIM_WHITE}dim{RESET} '
	)


# ansiExperiments()
# computeAvgAlsa()