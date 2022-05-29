import numpy as np
import matplotlib.pyplot as plt
from scipy.special import comb


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

