# compare binomial distribution functions from scipy.stats
# but also implement them myself

from scipy.stats import binom
import math


def binomialPMF(k: int, n: int, p: float) -> float:
	"""
	:param k: number of successes desired
	:param n: number of trials
	:param p: probability of success
	:return: probability of exactly k successes in n trials with success
	probability p
	"""

	# each success has probability p^k*(1-p)^(n-k)
	#	this means success chances multiplied by failure chances
	#	e.g. 2 successes of 6 trials at 60%: .6²*.4⁴
	probabilityOfEachSuccess: float = p**k * (1-p)**(n-k)

	# that's each success. how many ways are there to achieve them? ₙCₖ
	#   ₆C₂ is 6*5/2
	#   but the general form is in two parts:
	#   	n!/(n-k)! ← 6*5 possibilities: any slot for 1st success, 5 left for 2nd
	#		all over number of ways to arrange k objects: k!

	# note permutations is mathematically proven to be an integer
	permutations = math.factorial(n) / math.factorial(n-k)
	waysToArrange = math.factorial(k)
	nChooseK = permutations / waysToArrange

	return probabilityOfEachSuccess * nChooseK


def binomialCDF(k: int, n: int, p: float) -> float:
	# sum up all binomialPMFs up to and including k
	result = 0
	for i in range(0, k+1):
		result += binomialPMF(i, n, p)
	return result


# prevent imports from running this test code
if __name__ == "__main__":
	numTrials = 7  # Number of trials
	prob = 0.35  # Probability of success
	successes = 4  # Number of successes


	# compare manual calculations with library ones
	print(f'🐍 PMF: {binom.pmf(successes, numTrials, prob)}')
	print(f'🥝 PMF: {binomialPMF(successes, numTrials, prob)}')
	print(f'🐍 CDF: {binom.cdf(successes, numTrials, prob)}')
	print(f'🥝 CDF: {binomialCDF(successes, numTrials, prob)}')

