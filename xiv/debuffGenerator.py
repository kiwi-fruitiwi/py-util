# generate names for who gets what debuff for xiv encounters
from typing import List, Dict
from enum import Enum

playerNames: List[str] = ['kiwi', 'aerry', 'winry', 'cody']


# todo add isSupport method returning true if TANK|HEALER
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


def mokoScarletAuspice():
    # two stack markers on one support and one dps
    # stack first or spread first?
    # moko's cleave direction

    team: List = [
        Player('Kiwi', Job.SGE),
        Player('Aerry', Job.WAR),
        Player('Winry', Job.DRG),
        Player('Cody', Job.RDM)
    ]

    print(f'amr: moko ability → scarlet auspice')
    for player in team:
        print(f'{player.name:6} {player.job.value:10} {player.role.value}')


mokoScarletAuspice()