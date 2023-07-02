import math

import numpy as np
from scipy.integrate import quad

from scipy.integrate import quad
import matplotlib.pyplot as plt


def graphNormalDistribution():
    plt.style.use('dark_background')
    x = np.linspace(-4, 4, num=100)
    constant = 1.0 / np.sqrt(2 * np.pi)
    pdf_normal_distribution = constant * np.exp((-x ** 2) / 2.0)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(x, pdf_normal_distribution)
    ax.set_ylim(0)
    ax.set_title('Normal Distribution', size=20)
    ax.set_ylabel('Probability Density', size=20)

    plt.show()


def normalProbabilityDensity(x):
    coefficient = 1.0 / math.sqrt(2 * math.pi)
    return coefficient * math.exp((-x ** 2) / 2.0)


value: float = 99/300
print(quad(normalProbabilityDensity, value, np.PINF))
print(quad(normalProbabilityDensity, np.NINF, value))


# print(quad(normalProbabilityDensity, 0.85, np.PINF))

# while True:
#     lower_bound = float(input('enter lower integration bound'))
#     upper_bound = float(input('enter upper integration bound'))
#     print(quad(normalProbabilityDensity, lower_bound, upper_bound))

