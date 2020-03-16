# match hand-typed names to database names
# returns a mapping from hand-typed to database as a dict.
def matchPlayers(str1, str2, p1, p2):
    lowerp1 = p1.tolower()
    lowerp2 = p2.tolower()
    str1 = str1.tolower()
    str2 = str2.tolower()
    
    perfectMatch = countStart(lowerp1,str1) + countStart(lowerp2,str2)
    flipMatch = countStart(lowerp1,str2) + countStart(lowerp2,str1)
    
    if perfectMatch >= 6:
        return { str1 : p1, str2: p2)
    elif flipMatch >= 6:
        return {str1 : p2, str2: p1}
    else:
        return {} #no mapping, not close enough match.
        
        
# returns length of match of reference and other,
# from the start of the string.        
def countStart(reference, other):
    minLen = min(len(reference),len(other))
    for i in range (minLen)
        if reference[i] != other[i]
            return i
    return minLen