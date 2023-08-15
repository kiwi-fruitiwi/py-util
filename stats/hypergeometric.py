# see docs.scipy.org/doc/scipy/reference/generated/scipy.stats.hypergeom.html

from scipy.special import comb
import scipy.stats as ss


def hyperSingle(populationSize, sampleSize, successesInPop, successesInSample):
    """
    returns probability of n successes with popSize, sampleSize, successInPop
    :param populationSize: total number of cards remaining in deck
    :param sampleSize: number of draws
    :param successesInPop: successes in population. 15 lands remaining in deck
    :param successesInSample: successes we want in draws
    :return: probability of n successes in
    """
    hpd = ss.hypergeom(populationSize, sampleSize, successesInPop)
    return hpd.pmf(successesInSample)


def hyperUpTo(populationSize, sampleSize, successesInPop, k):
    """
    :return: probability of 1 to k successes in sample
    """
    accumulatedProbability: float = 0
    for i in range(1, k + 1):
        partialProbability = \
            hyperSingle(populationSize, sampleSize, successesInPop, i)
        print(f'🐳{i}: {partialProbability}')

        accumulatedProbability += partialProbability


    return accumulatedProbability


print(f'{hyperUpTo(33, 3, 15, 3)}')


# TODO understand the 3 expressions
def hypergeometricPMF(N, A, n, x):
    """
    Probability Mass Function for Hypergeometric Distribution
    :param N: population size
    :param A: total number of desired items in N
    :param n: number of draws made from N
    :param x: number of desired items in our draw of n items
    :returns: PMF computed at x
    """
    a_choose_x = comb(A, x)
    na_choose_x = comb(N - A, n - x)
    n_choose_n = comb(N, n)

    return a_choose_x * na_choose_x / n_choose_n