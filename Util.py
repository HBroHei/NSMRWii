def binToUtf(bytesSeq):
    return list(map(lambda l1:chr(l1),bytesSeq))

def convertNULL(char):
    if char=="\x00":
        return " "
    else:
        return char

def tilePosToObjPos(tilePos):
    return [tilePos[0]*16,tilePos[1]*16]

from math import ceil
def objPosToTilePos(objPos):
    return [ceil(objPos[0]/16),ceil(objPos[1]/16)]

import base64
# Thanks OpenAI
# Convert dict containing byte arrays into serialisable JSON data
def convertToJson(obj):
    if isinstance(obj, bytes):
        return base64.b64encode(obj).decode('utf-8')
    elif isinstance(obj, list):
        return [convertToJson(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: convertToJson(v) for k, v in obj.items()}
    else:
        return obj
# Convert JSON data back to dict with byte arrays
def convertToDict(obj):
    if isinstance(obj, str):
        try:
            return base64.b64decode(obj)
        except base64.binascii.Error:
            return obj
    elif isinstance(obj, list):
        return [convertToDict(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: convertToDict(v) for k, v in obj.items()}
    else:
        return obj