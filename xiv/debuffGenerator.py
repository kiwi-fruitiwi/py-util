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
    Player('Winry', Job.DRG),
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


# mokoScarletAuspice()
mokoShadowTwin()