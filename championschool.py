# utility methods to help with League of Legends learning
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

		# when _ or ' detected, next char is capitalized to comply with fandom wiki
		nextCharCaps: bool = False

		for ch in name:


			match ch:
				case '_':
					nextCharCaps = True
					nameBuilder += ch
					continue
				case '\'':
					nextCharCaps = True
					nameBuilder += ch
					continue
				case _:
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