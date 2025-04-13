from math import ceil

def binToUtf(bytesSeq):
    return list(map(lambda l1:chr(l1),bytesSeq))

def convertNULL(char):
    if char=="\x00":
        return " "
    else:
        return char

def tilePosToObjPos(tilePos):
    return [tilePos[0]*16,tilePos[1]*16]

def changeBytesAt(bytesStr:bytes, pos:int, newVal):
    tmp_bytearr = bytearray(bytesStr)
    print(newVal)
    tmp_bytearr[pos] = newVal
    return bytes(tmp_bytearr)

def changeNibbleAt(bytesStr:bytes, pos_nibble:int, newVal):
    pos = ceil(pos_nibble/2) - 1
    print(f"{bytesStr}, {pos_nibble}, {bytesStr[pos]}, {(newVal)} {(bytesStr[pos] & 0b00001111)}")
    return changeBytesAt(
        bytesStr,
        int(ceil(pos_nibble/2) - 1),
        ((newVal & 0b00001111) | (bytesStr[pos] & 0b11110000)) if pos_nibble%2==0 else ((newVal << 4) | (bytesStr[pos] & 0b00001111))
    )

def getNibbleAt(bytesStr:bytes, pos_nibble:int):
    pos = ceil(pos_nibble/2) - 1
    #print("GETTING at",pos,bytesStr[pos],(bytesStr[pos] & 0b11110000)>>4 if pos_nibble%2==1 else (bytesStr[pos] & 0b00001111))
    return (bytesStr[pos] & 0b11110000)>>4 if pos_nibble%2==1 else (bytesStr[pos] & 0b00001111)

def nibblesToByte(hnib,lnib):
    return (int(hnib)<<4) | int(lnib)

# Function to convert hex bytes to a formatted string
def hex_to_str(hex_bytes):
    return ''.join(f'{b:02}' for b in hex_bytes)
# Function to check if a pattern matches a hex string
def matches_pattern(hex_str, pattern):
    hex_str = hex_str.replace(' ', '')  # Remove spaces for comparison
    if len(hex_str) != len(pattern.replace(' ', '')):
        return False
    for h, p in zip(hex_str, pattern.replace(' ', '')):
        if p != 'x' and h != p:
            return False
    return True

from math import ceil,floor
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