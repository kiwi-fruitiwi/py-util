# utility methods to help with League of Legends learning
#   creates list of youtube channel links given champion name input

import string
from typing import List


def createWikiLinks():
	# read from champions.txt, stripping whitespace
	# instantiate wiki base URL

	championInput = open('champions.txt', 'r')
	championLines: List[str] = championInput.readlines()

	championNames: List[str] = []
	for line in championLines:
		name: str = line.strip()

		# TODO replace spaces with underscores, always capitalize tokens
		#   the first token is automatically capitalized by league wiki
		# iterate through each character after strip() → stringbuilder
		# encounter ' ': convert to '_', make next word capital
		# encounter
		name = name.replace(' ', '_')
		nameBuilder: str = ''

		nextCharCaps: bool = False

		# when _ or ' detected, next char capitalized to comply with fandom wiki
		for ch in name:
			if ch in ['_', '\'']:
				nextCharCaps = True
				nameBuilder += ch
				continue
			else:
				if nextCharCaps:
					nameBuilder += ch.upper()
					nextCharCaps = False
				else:
					nameBuilder += ch

		championNames.append(nameBuilder)

	# register URLs
	root = 'https://'
	for name in championNames:
		print(f'{root}leagueoflegends.fandom.com/wiki/{name}/LoL')
		print(f'{root}youtube.com/c/3MinuteLeagueofLegends/search?query={name}')
		print(f'{root}youtube.com/c/LoLDobby/search?query={name}')
		print(f'{root}youtube.com/c/MissFortuneDaBes/search?query={name}')
		print(f'{root}youtube.com/c/HappyChimeNoises/search?query={name}')
		print(f'{root}youtube.com/c/PekinWoof/search?query={name}')
		print(f'{root}youtube.com/c/Hoompty/search?query={name}')
		print(f'{root}youtube.com/c/LoLAnalyst/search?query={name}')


createWikiLinks()