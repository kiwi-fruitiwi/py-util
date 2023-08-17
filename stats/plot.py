# medium.com/analytics-vidhya/
# how-to-make-better-looking-charts-in-python-81058bd37ac3

# import libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def plotTest():
	# must precede data.plot
	sns.set_theme(style="darkgrid")

	# seaborn.pydata.org/generated/seaborn.dark_palette.html
	sns.dark_palette("#79C")

	# create and view data
	severity = ["High", "Medium", "Low"]
	freq = [10, 25, 50]
	data = pd.DataFrame(
		list(zip(severity, freq)),
		columns=['severity', 'freq'])

	# default matplotlib bar plot. get object and set grid
	ax = data.plot.bar(x="severity", y="freq")

	# default seaborn bar plot
	sns.barplot(data=data, x="severity", y="freq")

	# set x and y labels, title
	# if we have no xlabel call, matplotlib defaults to columnName
	# plt.xlabel('Accident Severity')
	plt.xlabel('')
	plt.ylabel('Number of Accidents')
	plt.title('Number of Accidents By Severity')

	# remove top and right borders. additional option for left border!
	sns.despine(left=True)

	# rotate both labels and axis name to 0º: horizontal
	plt.xticks(rotation=0)

	# set axes graduation label 'tick' sizes
	plt.xticks(size=14)
	plt.yticks(size=14)

	plt.show()


plotTest()