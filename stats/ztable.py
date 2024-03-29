import math

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from scipy.integrate import quad
from scipy.stats import norm
from typing import Set


def graphNormalDistribution():
	# plt.style.use('dark_background')
	sns.set_theme(style="darkgrid")
	sns.dark_palette("#79C")

	# remove top and right borders. additional option for left border!
	sns.despine(left=True)

	x = np.linspace(-4, 4, num=100)
	constant = 1.0 / np.sqrt(2 * np.pi)
	pdf_normal_distribution = constant * np.exp((-x ** 2) / 2.0)
	fig, ax = plt.subplots(figsize=(10, 5))

	ax.plot(x, pdf_normal_distribution)
	ax.set_ylim(0)
	ax.set_title('Normal Distribution', size=20)
	ax.set_ylabel('Probability Density', size=20)

	plt.show()


def normalTest():
	value: float = 99 / 300
	print(quad(normalProbabilityDensity, value, np.PINF))
	print(quad(normalProbabilityDensity, np.NINF, value))
	print(quad(normalProbabilityDensity, 0.85, np.PINF))


def scipyNormPlot():
	# evenly spaced numbers over an interval
	x = np.linspace(-5, 5, 1000)
	y = norm.pdf(x, 0, 1)  # μ=0, σ=1
	plt.plot(x, y)
	plt.title("Normal PDF with μ=0, σ=1")
	plt.show()


def normalProbabilityDensity(x):
	coefficient = 1.0 / np.sqrt(2 * np.pi)
	return coefficient * math.exp((-x ** 2) / 2.0)


def safeEval(expression: str) -> float:
	allowedChars: Set = set('0123456789.+-*/() ')
	if set(expression) <= allowedChars:
		try:
			return eval(expression)
		except Exception as e:
			print(f'Error: {e}')
	else:
		print(f'Invalid characters in expression.')


def areaBetweenZScores():
	print(f'')
	first: str = input('lower integration bound → ')
	second: str = input('upper integration bound → ')

	try:
		lowerBound: float = safeEval(first)
		upperBound: float = safeEval(second)

		# compute the definite integral
		print(f'🐳 evaluating pdf: [{lowerBound:.2f}, {upperBound:.2f}]')

		# quad returns a tuple with the error in index 1. we only need
		# the definite integral value itself in index 0
		print(quad(normalProbabilityDensity, lowerBound, upperBound)[0])
	except Exception as e:
		print(f'Error: {e}')


# When you use norm.ppf(0.40), you're asking: "What is the z-score such that
# 40% of the data in a standard normal distribution falls below it?"
def reverseNormalCalcs():
	print(f'')
	percentileInput: str = input('percentage of data → ')

	try:
		percentile: float = safeEval(percentileInput)
		print(f'z-score for {percentile*100:.2f}: {norm.ppf(percentile)}')

	except Exception as e:
		return f'Error: {e}'


# menu system for selecting between integrating between z-scores and norm.ppf
def main():
	done: bool = False
	while not done:
		userInput: str = input(
			f'\n'
			f'1. integrate between z-scores\n'
			f'2. find z-score based on percentile\n'
			f'→ ')

		allowedChars: Set = set('12')
		if set(userInput) <= allowedChars:
			try:
				match userInput:
					case '1':
						areaBetweenZScores()
					case '2':
						reverseNormalCalcs()
					case _:
						print(f'🐳 This should not occur :P')
			except Exception as e:
				print(f'Error: {e}')
		else:
			print(f'🐳 invalid choice')


main()