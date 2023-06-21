# find the closest string match from an input and given list of strings

import difflib
import json
from typing import List


def find_closest_match(subject: str, target: List[str]):
    closestMatch = difflib.get_close_matches(subject, target, n=1)
    if closestMatch:
        return closestMatch[0]
    else:
        return None


input_string = "rivary"

with open('ratings.json') as file:
    data = json.load(file)

print(f'{data.keys()}')

bestMatch = find_closest_match(input_string, data.keys())

if bestMatch:
    print(f"Closest match to '{input_string}' is '{bestMatch}'")
else:
    print(f"No close match found for '{input_string}'")