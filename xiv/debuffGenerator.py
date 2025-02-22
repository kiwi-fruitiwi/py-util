# generate names for who gets what debuff for xiv encounters
import random
from typing import List, Dict
from enum import Enum

playerNames: List[str] = ['kiwi', 'aerry', 'winry', 'cody']


class Direction(Enum):
    FRONT = 'Front'
    BACK = 'Back'
    LEFT = 'Left'
    RIGHT = 'Right'


class Role(Enum):
    TANK = 'Tank'
    HEALER = 'Healer'
    DPS = 'DPS'


class Job(Enum):
    WHM = 'White Mage'
    SGE = 'Sage'
    AST = 'Astrologian'
    SCH = 'Scholar'

    WAR = 'Warrior'
    DRK = 'Dark Knight'
    PLD = 'Paladin'
    GNB = 'Gunbreaker'

    DRG = 'Dragoon'
    SAM = 'Samurai'
    NIN = 'Ninja'
    MNK = 'Monk'
    RPR = 'Reaper'

    MCH = 'Machinist'
    DNC = 'Dancer'
    BRD = 'Bard'

    RDM = 'Red Mage'
    BLM = 'Black Mage'
    SMN = 'Summoner'

    def getRole(self):
        return jobToRole[self]


jobToRole: Dict[Job, Role] = {
    Job.WHM: Role.HEALER,
    Job.SGE: Role.HEALER,
    Job.AST: Role.HEALER,
    Job.SCH: Role.HEALER,

    Job.WAR: Role.TANK,
    Job.DRK: Role.TANK,
    Job.PLD: Role.TANK,
    Job.GNB: Role.TANK,

    Job.DRG: Role.DPS,
    Job.SAM: Role.DPS,
    Job.NIN: Role.DPS,
    Job.MNK: Role.DPS,
    Job.RPR: Role.DPS,

    Job.MCH: Role.DPS,
    Job.DNC: Role.DPS,
    Job.BRD: Role.DPS,

    Job.RDM: Role.DPS,
    Job.BLM: Role.DPS,
    Job.SMN: Role.DPS
}


class Player:
    def __init__(self, name, job):
        self.name = name
        self.job = job
        self.role = job.getRole()


team: List = [
    Player('Kiwi', Job.SGE),
    Player('Aerry', Job.WAR),
    Player('Winry', Job.MCH),
    Player('Cody', Job.RDM)
]


# arms and double cleave mechanic with binary proximity bait
# 💎 mechanics: shadow-twin → triple kasumi-giri → azure auspice
# 	tether adjust: NE, SW
# 	arm location → rotate if necessary
# 	second cleave directions: 2 after first back
# 	near vs far proximity for bind
#
# 	variables:
# 		tether. completely random and need to adjust, like scurrySpark
# 		arm location: binary
# 		second cleave directions: front back left right
# 		near vs far proximity bait and bind
def mokoShadowTwin():
    print(f'🫂 amr mechanic: moko → shadow twin')

    # tether. completely random and need to adjust, like scurrySpark
    tetheredPlayers: List[str] = [player.name for player in random.sample(team, 2)]
    print(f'\ttethers on → {tetheredPlayers}')

    # arm location: binary
    locations: List[str] = ['W-E hands', 'N-S hands']
    print(f'\t{random.choice(locations)}')

    # second cleave directions: front back left right
    print(f'\tsecond cleave: {random.choice(list(Direction)).value.lower()}')

    # near vs far proximity bait and bind
    proximity: List[str] = ['close', 'far']
    print(f'\tproximity marker: {random.choice(proximity)}')


# four expanding fire lines with stack and spread
# variables
#   stack first vs spread first
#   stack markers don't matter! because it's always one from each support or dps
#   one person gets a cleave marker
#   where do the first two fire lines intersect?
#   🕯️ how does this affect permutations for where to go after cleave?
def mokoScarletAuspice():
    # two stack markers on one support and one dps
    # stack first or spread first?

    print(f'\nTeam Composition: ')
    for player in team:
        print(f'{player.name:6} {player.job.value:10} {player.role.value}')
    print(f'')


    print(f'🔥 amr mechanic: moko → scarlet auspice')
    # stack first or spread first?
    print(f"\t{random.choice(['stack', 'spread'])} first")

    # get stack markers from random unique samples
    supportPlayers = \
        [player for player in team if player.role in (Role.HEALER, Role.TANK)]
    dpsPlayers = [player for player in team if player.role == Role.DPS]

    # randomly select one player from each group
    selectedSupport = random.choice(supportPlayers)
    selectedDPS = random.choice(dpsPlayers)

    print(f'\tstack markers on → {selectedSupport.name} and {selectedDPS.name}')

    # print the cleave direction of moko or his adds
    print(f'\tcleave direction: {random.choice(list(Direction)).value.lower()}')


# each player gets 🟥red or 🟦blue (clockwise or counterclockwise) rotation for
# their personal portal, which faces either West or East
#
# "red north, blue south"
# "west out, east in" or "left out, right in" when facing north
# one of these portals is your friend. the other one kills you.
#   players on the outside (west / left personal teleporters) stand directly on
#   spinny part of outside portal. inner partner stands where that portal
#   rotates to
def zelessInfernBrand3():
    print(f'🫂 zeless gah mechanic: infern brand 3')
    print(f'personal portal → {random.choice(["East", "West"])}')
    print(f'debuff color → {random.choice(["🟥", "🟦"])}')
    print(f'end')


# widening or narrowing first, then alternate for 3 more
# near or far first, then alternate for 3 more
# permutations
#   widening far: healers out
#   narrowing near: tanks in → healers out
#   narrowing far: bait on waymarks → healers first
#   widening near: bait on waymarks → tanks first
def witchHunt():
    print(f'\n')
    print(f'M4S.⚡: widening or narrowing witch hunt')
    print(f'AoE: {random.choice(["widening", "narrowing"])}')
    print(f'bait: {random.choice(["near", "far"])}')
    pass


# electrope edge 2: cage, spark, cage
# variables: 2 or 3 count, long vs short, spread or stack
def electropeEdge2():
    print(f'\n')
    print(f'M4S.⚡: EE2')
    print(f'number of hits: {random.choice(["2", "3"])}')
    print(f'timer: {random.choice(["short", "long"])}')
    print(f'ss: {random.choice(["stack", "spread"])}')
    pass


#
def diamondDust():
    print(f'\n')
    print(f'🪽FRU.P2: Diamond Dust')
    print(f'  speech: {random.choice(["cleave", "reap"])}')
    print(f'  first circle spawn: {random.choice(["cardinals", "intercards"])}')
    print(f'  {random.choice(["marked", "unmarked"])}')


diamondDust()
# witchHunt()
# electropeEdge2()
# mokoScarletAuspice()
# mokoShadowTwin()
# zelessInfernBrand3()

















