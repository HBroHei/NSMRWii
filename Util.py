def binToUtf(bytesSeq):
    return list(map(lambda l1:chr(l1),bytesSeq))

def convertNULL(char):
    if char=="\x00":
        return " "
    else:
        return char

def tilePosToObjPos(tilePos):
    return [tilePos[0]*16,tilePos[1]*16]

def objPosToTilePos(objPos):
    return [objPos[0]//16,objPos[1]//16]