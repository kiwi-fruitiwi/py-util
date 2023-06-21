import Levenshtein # makes finding the L-distance between strings much faster
from fuzzywuzzy import process
import json

# load json from our 17L csv to json converter
with open('ratings.json') as file:
    data = json.load(file)

bestMatches = process.extractBests("arwen", data.keys())
[print(e) for e in bestMatches]