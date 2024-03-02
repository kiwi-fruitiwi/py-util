import dataFetcher
import dataConverter
import dataAggregator
from datetime import datetime

dataFetcher.fetch()
dataConverter.convert()
dataAggregator.aggregate()

# Print the current date and time
print(datetime.now())