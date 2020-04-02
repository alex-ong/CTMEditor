'''Convert between spreadsheet to class'''
class ScoreEntry(object):
    def __init__(self, data):
        self.seed = data[1]
        self.twitch = data[0]
        self.discord = None
        self.country = data[3]
        self.score = data[4]
    
    def findDiscord(self, usercontext):
        pass