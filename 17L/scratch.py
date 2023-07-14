# scratch file for making small computations
# 1. average ALSA

import json
import statistics
from typing import Dict, List


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


computeAvgAlsa()