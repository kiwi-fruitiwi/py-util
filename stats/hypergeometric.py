# see docs.scipy.org/doc/scipy/reference/generated/scipy.stats.hypergeom.html

import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as ss

from constants import ANSI
from typing import List


def hypergeoPMF(deckSize, drawSteps, hits, k):
    """
    returns probability of n successes with popSize, sampleSize, successInPop
    :param deckSize: total number of cards remaining in deck
    :param drawSteps: number of draws
    :param hits: successes in population. 15 lands remaining in deck
    :param k: successes we want in draws
    :return: probability of successes in sample
    """
    hpd = ss.hypergeom(deckSize, drawSteps, hits)
    return hpd.pmf(k)


def hypergeoCDF(deckSize, drawSteps, hits, k):
    """
    sums up hypergeometric PMF values to come up with cumulative density
    :return: probability of 1 to k successes in sample
    """

    # note this does not include 0 successes; we start at 1. otherwise we
    # return 1 all the time
    partialProbabilities: List[float] = \
        [hypergeoPMF(deckSize, drawSteps, hits, x) for x
         in range(1, k + 1)]

    length: int = len(partialProbabilities)
    runningSum = [sum(partialProbabilities[:i+1]) for i in range(length)]

    for i in range(len(partialProbabilities)):
        print(f'draw {i+1}  → {partialProbabilities[i]*100:>5.1f}%')

    return sum(partialProbabilities)


def hypergeoPlot(N, A, n):
    """
    Visualization of Hypergeometric Distribution for given parameters
    :param N: population size
    :param A: total number of desired items in N
    :param n: number of draws made from N
    :returns: Plot of Hypergeometric Distribution for given parameters
    """
    plt.style.use('dark_background')

    x = np.arange(1, n + 1)
    y = [hypergeoPMF(N, A, n, x) for x in range(1, n + 1)]

    # probably should use accumulate from itertools
    # → runningSum = list(accumulate(y))
    runningSumOfY = [sum(y[:i+1]) for i in range(len(y))]

    plt.plot(x, runningSumOfY, 'bo')
    plt.vlines(x, 0, runningSumOfY, lw=2)
    plt.xlabel('# of desired items in our draw')
    plt.ylabel('Probabilities')
    plt.title('Hypergeometric Distribution Plot')
    plt.show()


# don't run this on imports
if __name__ == '__main__':
    done: bool = False

    while not done:
        userInput: str = input('library draws successPop hitsDesired: ')
        inputs: List[str] = userInput.split(' ')
        deckSize: int = int(inputs[0])
        drawSteps: int = int(inputs[1])
        totalHits: int = int(inputs[2])
        hitsDesired: int = int(inputs[3])

        totalChances: str = f'{hypergeoCDF(deckSize, drawSteps, totalHits, hitsDesired) * 100:>5.1f}%'
        print(f'draw 1 to max → {totalChances}\n')