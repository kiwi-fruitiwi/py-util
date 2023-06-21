import Levenshtein # makes finding the L-distance between strings much faster
from fuzzywuzzy import process
from typing import List
import json

# load json from our 17L csv to json converter
with open('ratings.json') as file:
    data = json.load(file)

done: bool = False

while not done:
    userInput: str = input('\nEnter cards: ')

    # split the input string into a list using ',' as delimiter
    names = userInput.split(',')

    # trim leading and trailing whitespace
    values = [name.strip() for name in names]

    # set up list of card names matched to our input
    cardFetchList: List[str] = []

    for value in values:
        # extractBests returns a list of tuples
        #   → [print(e) for e in bestMatches] results in the following:
        #       ('Aragorn, the Uniter', 90)
        #       ('Gimli, Counter of Kills', 75)
        #       ('Legolas, Counter of Kills', 75)
        #       ('Mordor Muster', 66)
        #       ('Bitter Downfall', 60)
        bestMatches = process.extractBests(value, data.keys())
        bestMatchTuple = bestMatches[0]

        # we want the name part of the best match. we could use extractOne :P
        bestMatchName = bestMatchTuple[0]
        cardFetchList.append(bestMatchName)

    # use cardFetchList to grab JSON data from data variable
    [print(name) for name in cardFetchList]