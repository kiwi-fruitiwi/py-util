# medium.com/analytics-vidhya/
# how-to-make-better-looking-charts-in-python-81058bd37ac3

# import libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def plotTest():
	# create and view data
	severity = ["High", "Medium", "Low"]
	freq = [10, 25, 50]
	data = pd.DataFrame(list(zip(severity, freq)), columns=['severity', 'freq'])

	# default matplotlib bar plot
	data.plot.bar(x="severity", y="freq")

	# default seaborn bar plot
	# sns.barplot(data=data, x="severity", y="freq")
	plt.show()


plotTest()