#given a hand typed winner, returns whether it is p1 or p2
def matchPlayers(winner, p1, p2):
    lowerp1 = p1.lower()
    lowerp2 = p2.lower()
    winner = winner.lower()
    
    perfectMatch = countStart(lowerp1,winner)
    flipMatch = countStart(lowerp2,winner)
    
    if perfectMatch >= 3 and perfectMatch > flipMatch:
        return "P1"
    elif flipMatch >= 3:
        return "P2"
    else:
        return None
        
        
# returns length of match of reference and other,
# from the start of the string.        
def countStart(reference, other):
    minLen = min(len(reference),len(other))
    for i in range (minLen):
        if reference[i] != other[i]:
            return i
    return minLen