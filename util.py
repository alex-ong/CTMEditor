import os
from enum import Enum


class LEAGUES(Enum):
    ME = 0
    CC = 1
    FC = 2
    CT1 = 3
    CT2 = 4
    CT3 = 5
    CT4 = 6
    CT5 = 7


# convert from enum to string
def leagueString(leagues):
    if leagues == LEAGUES.ME:
        return "me"
    elif leagues == LEAGUES.CC:
        return "cc"
    elif leagues == LEAGUES.FC:
        return "fc"
    elif leagues == LEAGUES.CT1:
        return "ct1"
    elif leagues == LEAGUES.CT2:
        return "ct2"
    elif leagues == LEAGUES.CT3:
        return "ct3"
    elif leagues == LEAGUES.CT4:
        return "ct4"
    elif leagues == LEAGUES.CT5:
        return "ct5"
    else:
        return None


def modulePath():
    return os.path.dirname(os.path.realpath(__file__))
