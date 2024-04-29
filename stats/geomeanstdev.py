import math


# noinspection NonAsciiCharacters
def find_μσ(probability: float):

	p: float = probability
	μ: float = 1/p
	σ: float = math.sqrt(1-p) / p

	print(f'μ:{μ:.1f} σ:{σ:.1f}')


# don't run this on imports
if __name__ == '__main__':
	done: bool = False

	while not done:
		userInput: str = input('\nprobability: ')
		find_μσ(float(userInput))