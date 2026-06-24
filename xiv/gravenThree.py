import random

pairs = [
    ("⬆️", "⬆️"),  # up up
    ("⬆️", "➡️"),  # up right
    ("➡️", "➡️"),  # right right
    ("➡️", "⬇️"),  # right down
    ("⬇️", "⬇️"),  # down down
    ("⬇️", "⬅️"),  # down left
    ("⬅️", "⬅️"),  # left left
    ("⬅️", "⬆️"),  # left up
]

while True:
    pair = list(random.choice(pairs))
    random.shuffle(pair)
    print("".join(pair), end="")
    input()