from .util import modulePath
from os.path import join
import json
import collections

FILE = "channelinfo.json"
DATA = None


def _loadSettings():
    with open(join(modulePath(), FILE)) as f:
        data = json.load(f, object_pairs_hook=collections.OrderedDict)
    result = {}
    for key in data:
        result[key] = ChannelSummaryCache(data[key])
    return result


def GetSummarySettings():
    global DATA
    if DATA is None:
        DATA = _loadSettings()
    return DATA


def SaveSummarySettings():
    result = {}
    for key in DATA:
        result[key] = DATA[key].toDictionary()

    with open(join(modulePath(), FILE), "w") as f:
        json.dump(result, f, indent=4)


class ChannelSummaryCache(object):
    def __init__(self, data):
        self.name = data["name"]
        self.channelID = data["channelID"]
        self.messages = data["messages"]

    def safeRetrieve(self, data, key):
        return data[key] if len(data[key]) > 0 else None

    def toDictionary(self):
        return {
            "name": self.name,
            "channelID": self.channelID,
            "messages": self.messages,
        }
