# create a json file with 🔑cardName and ALSA = value: float from requests/all
# within a more recent timeframe than dataFetch.py
#
# target input json, but with new request: &start_date=
# 	data/requests/all/all.json
#	data/requests/top/all.json
#
# target output json:
#	data/allRecentAlsaUpdate.json
#	data/topRecentAlsaUpdate.json
#
# the goal here is to update ALSA values with the last week or two
# we assume here that the ALSA value is always a float and never null


