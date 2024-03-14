import Util
from math import floor
nodesList = []

# NOTE: This file is modified to work with the randomizer
# The actual file that works independently is u8.py

template_u8 = {"Raw Data":b"","File Name List":[],"Number of area":-1}

"""
A class used to store individual properties of U8 archives
@param {Boolean} isFile True if the object is a file, False if it is a directory
@param {Int} fileNameIdx The offset for the name string
@param o4 Data of 0x04: offset of data (File) / parent dir index (Dir)
@param o8 Data of 0x08: Size of data (File) / Next Node Index (Dir)
"""
class U8Arc:
    def __init__(self,isFile,fileNameIdx,o4,o8,fileName="",parentDir = -1):
        self.isFile = isFile
        self.fileNameIdx = fileNameIdx
        if isFile:
            self.beginDataOffset = o4
            self.dataSize = o8
            self.parentDirIdx = 0
            self.nextNodeIdx = 0
        else:
            self.parentDirIdx = o4
            self.nextNodeIdx = o8
            self.beginDataOffset = 0
            self.dataSize = 0
        self.fileName = fileName
        #self.parentDir = parentDir

def errMsgFilevaild(msg):
    print("Not a valid ARC file: " + msg)
    exit(0)

# Obsolute function since I did not know b"\x00"*8 is a thing
def genx00(num):
    returnB = b""
    for _ in range(1,num):
        returnB += b"\x00"
    return returnB

###################################################################################

def checkFileDir(byteFile,pos,isRoot=False):
    ### CHECK IS FILE/DIR ###
    typeCheckDigit = byteFile[pos]
    if typeCheckDigit==0:
        #FILE HANDLING
        fileHandle(byteFile,pos)
    elif typeCheckDigit==1:
        #DIRECTORY HANDLING
        dirHandle(byteFile,pos,isRoot)
    else:
        errMsgFilevaild("Archive did not recognize any folders or files")

def fileHandle(byteFile,offset):
    fileNameIdx = int.from_bytes(byteFile[offset+1:offset+4],"big")
    beginDataOffset = int.from_bytes(byteFile[offset+4:offset+8],"big")
    dataSize = int.from_bytes(byteFile[offset+8:offset+12],"big")
    nodesList.append(U8Arc(True,fileNameIdx,beginDataOffset,dataSize))


def dirHandle(byteFile,offset,isRoot=False):
    global pointer
    pointer = offset+3
    if not isRoot:
        #Get the name
        #Note that root does not have name
        fileNameIdx = int.from_bytes(byteFile[offset+1:offset+4],"big")
    else:
        fileNameIdx = -1
    
    # Get the parent index
    # Returns 0 if the dir is at root
    pointer = offset+7
    parentDirIdx = int.from_bytes(byteFile[offset+4:offset+8],"big")
    if not isRoot:
        #Get the next file in node
        pointer = offset+11
        nextNodeIdx = int.from_bytes(byteFile[offset+8:offset+12],"big")
        #Store the propereties
        nodesList.append(U8Arc(False,fileNameIdx,parentDirIdx,nextNodeIdx))
        #print(nodesList[0].fileName)



def openFile(ARCfileName,orginalFileName=""):
    global nodesList

    ### OPEN FILE ###
    bfile = open(ARCfileName,"rb")
    byteFile = bfile.read()
    bfile.close()

    ### CHECK HEADER TEXT ###
    pointer = 3
    headerHex = byteFile[0:pointer+1].hex() #pointer+1 = 4
    if str(headerHex)!="55aa382d":
        errMsgFilevaild("Header not 'Uª8-'")

    ### CHECK OFFSET TO FIRST NODE ###
    pointer = 7
    offsetFirstNode = int.from_bytes(byteFile[4:pointer+1],"big")

    ### CHECK SIZE OF ALL NODES ###
    pointer = 11
    sizeAllNodes = int.from_bytes(byteFile[8:pointer+1],"big")

    ### CHECK OFFSET OF FILE DATA ###
    pointer = 15
    offsetFileData = int.from_bytes(byteFile[12:pointer+1],"big")

    #print(byteFile[12:pointer+1],offsetFileData)
    form = "{:<10}: {:<3} - {:<3} = {:<3} , /8 = {:<2}"
    #print(form.format(orginalFileName,offsetFileData,offsetFirstNode+sizeAllNodes,offsetFileData-(offsetFirstNode+sizeAllNodes),(offsetFileData-(offsetFirstNode+sizeAllNodes))//8))
    #print("data",byteFile[:offsetFileData])

    ### FILE/DIR HANDLING ###
    pointer = offsetFirstNode


    offset = offsetFirstNode
    pointer = offset+3
    
    # Get the parent index
    # Returns 0 if the dir is at root
    pointer = offset+7
    parentDirIdx = int.from_bytes(byteFile[offset+4:offset+8],"big")

    #Get the total number of entries included (Directory/files)
    pointer = offset+11
    nodeTot = int.from_bytes(byteFile[offset+8:offset+12],"big")
    #print("Total number of files:",nodeTot)

    # Get the number of areas
    # After byte name, a bunch of \x00 will appear
    # They are usually in the multple of 8, i.e.16,32,8
    # Divide the number by 8, you will get the number of area(s) of that level.
    x00Num = offsetFileData-(offsetFirstNode+sizeAllNodes)
    noAreas = floor(x00Num/8)
    #print(offsetFileData,(offsetFirstNode+sizeAllNodes))

    # For Root: loop through each dir/files
    # (Each nodes are placed next to each other, forming an array/list)
    #print("Loading sub-directories...")
    for i in range(1,nodeTot):
        pointer = pointer+12
        checkFileDir(byteFile,offset+(12*i))

    ### GET FILE NAMES ###
    strNameOffset = pointer
    startOfStr = strNameOffset+nodesList[0].fileNameIdx
    endOfStr = offsetFirstNode+sizeAllNodes
    #print(byteFile[startOfStr:endOfStr])
    fNames_ = Util.binToUtf(byteFile[startOfStr:endOfStr])
    fNames = list(filter(None,"".join(list(map(Util.convertNULL,fNames_))).split(" ")))
    # Note: due to decode() does not return the NULL value, custom method is used
    returnList = {"Raw Data":byteFile,"File Name List":fNames,"Number of area":noAreas}
    for i in range(0,len(nodesList)):
        nodesList[i].fileName = fNames[i]
        #print("File ",i,":",nodesList[i].fileName)
        
        returnList[nodesList[i].fileName] = {
            "Name":nodesList[i].fileName,
            "Offset":nodesList[i].beginDataOffset,
            "Size":nodesList[i].dataSize,
            "isFile":nodesList[i].isFile,
            "ParentDir":nodesList[i].parentDirIdx,
            "NextNode":nodesList[i].nextNodeIdx,
            "Data":byteFile[nodesList[i].beginDataOffset:nodesList[i].beginDataOffset+nodesList[i].dataSize]
        }
        #print(nodesList[i+1].beginDataOffset-(nodesList[i].beginDataOffset+nodesList[i].dataSize))

    nodesList = []
    return returnList

########################################################

def saveByteData(fileName,data):
    u8f = open(fileName,"wb")
    u8f.write(data)
    u8f.close()

def printByteData(fileName):
    bfile = open(fileName,"rb")
    byteFile = bfile.read()
    bfile.close()
    print(byteFile)

def openByteData(fileName):
    bfile = open(fileName,"rb")
    byteFile = bfile.read()
    bfile.close()
    return byteFile

def saveTextData(fileName,data):
    tf = open(fileName,"w")
    tf.write(data)
    tf.close()

def splitWithEachEle(data):
    returnData = ""
    for i_ in data:
        returnData += hex(i_) + "\n"
    return returnData

###########################################################


def repackToBytes(u8List):
    #         FileMagic OffsetTo1stNode
    #                   -Always 0x20, rep. by the space char below
    byteHead = b"U\xaa8-\x00\x00\x00 "
    nodes = b""
    byteNames = b""
    fileDatas = b""
    returnARC = b""
    # Add root directory
    #          isDir    StrName        ParentDir           NextNode(number of nodes)
    nodes += b"\x01\x00\x00\x00\x00\x00\x00\x00" + (len(u8List["File Name List"])+1).to_bytes(4,"big") #Root Node
    #print(len(u8List["File Name List"]),":",u8List["File Name List"])

    #TODO SOMETHING IS WORNG WITH HEAD SIZE WHICH AFFECTS THE JUDGEMENT OF WHERE THE STRING TABLE ENDS. FIX IT

    # "Predict" the length of header
    #                                    Node Size   RootNodeSize  Offset         String Name Section Size Offset   
    pHeadSize = (len(u8List["File Name List"]))*12 +         12 + 1 + (len("0".join(u8List["File Name List"]))) + 1 
    # The start of the file data
    pFileDataOffset = 32 + pHeadSize + u8List["Number of area"]*8
    firstFileDataOffset = pFileDataOffset
    for istr in u8List["File Name List"]:
        # 1. Node type: defaults to file
        # 2. Offset for the file name relative to the start of string pool
        # FOR FILES:
        # 3. Offset to beginning of data
        # 4. Size of the data
        # FOR DIRECTORY:
        # 3. Parent node index
        # 4. Next node offset that is not in its directory
        nodeDetails = [b"\x00",b"",b"",b""]
        
        if not u8List[istr]["isFile"]: # It is a directory
            #print("hvfguyihgyvc")
            nodeDetails[0] = b"\x01"
            nodeDetails[2] = u8List[istr]["ParentDir"].to_bytes(4,"big")
            #print("DIR:",istr,u8List[istr]["NextNode"])
            nodeDetails[3] = u8List[istr]["NextNode"].to_bytes(4,"big")
        else:
            nodeDetails[2] = (pFileDataOffset).to_bytes(4,"big") # Offset to first data.
            # pFileDataOffset will be changed below
            nodeDetails[3] = len(u8List[istr]["Data"]).to_bytes(4,"big")

        #The string pool offsets are relative to the start of the string pool. (From wiki.tockdom.com)
        # Also offsetted by 0x01
        # Initally (index(istr)==0), len(byteNames) should return 0
        nodeDetails[1] = (len(byteNames)+1).to_bytes(3,"big")
        byteNames += bytes(istr,"utf_8") + b"\x00"
        #print("Name List:",byteNames)
        #print("nodeDetails",nodeDetails)
        # Put all the byte arrays together to form a node
        nodes += nodeDetails[0]+nodeDetails[1]+nodeDetails[2]+nodeDetails[3]

        # Add all the files data
        fileDatas += u8List[istr]["Data"]
        # File data ENDS offset now have incremented
        pFileDataOffset += len(u8List[istr]["Data"])
    
    headSize = (len(nodes)+1+len(byteNames))
    # Check whether Expected head size == Observed head size
    assert pHeadSize==headSize, "Head Size not match" 
    fileNodeOffset = (headSize + 32).to_bytes(4,"big") #32 = Offset to first node
    #           Size of All Nodes             file offset                             (reserved)
    byteHead += pHeadSize.to_bytes(4,"big") + firstFileDataOffset.to_bytes(4,"big") + b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" #\x00 for 16
    returnARC += byteHead + nodes + b"\x00" + byteNames
    #print("Before",byteNames)
    # Insert the \x00 for the number of areas
    #returnARC += genx00(u8List["Number of area"]*8) OBSOLUTED
    returnARC += b"\x00" * 8 * u8List["Number of area"]
    #print(b"\x00" * 8 * u8List["Number of area"])
    # if u8List["Number of area"]*8!=0:
    #     returnARC += b"\x00"
    # Insert File Data
    returnARC += fileDatas

    #print(genx00(u8List["Number of area"]*8))
    
    return returnARC

# function ONLY works for NSMBW level archives
def constructArchiveFile_m(file_name, file_data, isDir = False, nextNode = 0):
    # Some proerties are missing due to the fact that they are not required for repacking them to an U8 Arc
    # TODO maybe I can make it compatible with other U8 archives in the future?
    return {
        "Name" : file_name,
        # No Offset
        # No Size
        "isFile" : not isDir,
        "ParentDir" : 0,
        "NextNode" : nextNode,
        "Data" : file_data
    }

def constructFromScratch(noAreas,fileList):
    ''' Template Dict structure
    {"Raw Data":b"","File Name List":[],"Number of area":-1}
    returnList[nodesList[i].fileName] = {
            "Name":nodesList[i].fileName,
            "Offset":nodesList[i].beginDataOffset,
            "Size":nodesList[i].dataSize,
            "isFile":nodesList[i].isFile,
            "ParentDir":nodesList[i].parentDirIdx,
            "NextNode":nodesList[i].nextNodeIdx,
            "Data":byteFile[nodesList[i].beginDataOffset:nodesList[i].beginDataOffset+nodesList[i].dataSize]
    }
    '''
    returnData = {
        # Skips orginal Raw Data
        "File Name List" : [fileDat["Name"] for fileDat in fileList],
        "Number of area" : noAreas,
    }
    for fileDat in fileList:
        returnData[fileDat["Name"]] = fileDat
    
    return returnData

#openFile("Stage/01-01.arc")
#printByteData("test1.arc")
#print(int.from_bytes(b"`","big"))

