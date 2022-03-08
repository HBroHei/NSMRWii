def binToUtf(bytesSeq):
    return list(map(lambda l1:chr(l1),bytesSeq))

def convertNULL(char):
    if char=="\x00":
        return " "
    else:
        return char

