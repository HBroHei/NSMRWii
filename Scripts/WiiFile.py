import Util

def errMsgFilevaild(msg):
    print("Not a valid BRLYT file: " + msg)
    exit(0)

def BRLYTFile(byteData):
    ### CHECK HEADER TEXT ###
    pointer = 3
    headerStr = "".join(Util.binToUtf(byteData[0:pointer+1])) #pointer+1 = 4
    if headerStr!="RLYT":
        errMsgFilevaild("Header not 'RLYT'")
    
    ### CHECK BOM ###
    if byteData[4]==254 and byteData[5]==255:
        b_o_m = "big"
    elif byteData[4]==255 and byteData[5]==254:
        b_o_m = "little"
    else:
        errMsgFilevaild("Byte Order Mark is not found")
    print("Byte order mark:",b_o_m,"endian")

    ### LENGTH OF THE FILE ###
    pointer = 11
    fileLen = int.from_bytes(byteData[8:pointer+1],b_o_m)
    print("File Length:",fileLen)

    ### LENGTH OF THE HEAADER ###
    pointer = 13
    headLen = int.from_bytes(byteData[12:pointer+1],b_o_m)
    print("Header Length:",headLen)

    ### NUMBER OF SECTIONS ###
    pointer = 15
    noSecs = int.from_bytes(byteData[14:pointer+1],b_o_m)
    print("Number of Sections:",noSecs)

    ### END OF HEADER ###

    ### SECTIONS ###
    pointer = 16
    for _ in range(1,noSecs):
        curSec = "".join(Util.binToUtf(byteData[pointer:pointer+4]))
        print("Section " + str(_) + ". \nMagic:",curSec)
        if curSec == "lyt1":
            ### LYT1 FILE PROCESSING ###

            ###
            pass
    