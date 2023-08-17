import math

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from scipy.integrate import quad
from scipy.stats import norm


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


def main():
	done: bool = False
	while not done:
		print(f'')
		lower_bound = float(input('lower integration bound → '))
		upper_bound = float(input('upper integration bound → '))

		# compute the definite integral
		print(quad(normalProbabilityDensity, lower_bound, upper_bound))


main()