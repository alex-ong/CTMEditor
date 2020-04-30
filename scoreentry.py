"""Convert between spreadsheet to class"""


class ScoreEntry(object):
    def __init__(self, data):
        self.seed = data[1].value
        self.twitch = data[0].value
        self.discord = None
        self.country = data[4].value
        self.score = data[5].value

    def findDiscord(self, usercontext):
        pass
