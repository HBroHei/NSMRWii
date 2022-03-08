import Util
import WiiFile
import nsmbw

ARCfileName = "Stage/01-01.arc" #"Stage/01-02.arc"

nextNode = -1
i = 0
nodesList = []
pointer = 0

offsetFirstNode=0
sizeAllNodes = 0

byteFile = []

"""
A class used to store individual properties of U8 archives
@param {Boolean} isFile True if the object is a file, False if it is a directory
@param {Int} fileNameIdx The offset for the name string
@param o4 Data of 0x04: offset of data (File) / parent dir index (Dir)
@param o8 Data of 0x08: Size of data (File) / Next Node Index (Dir)
"""
class U8Arc:
    def __init__(self,isFile,fileNameIdx,o4,o8,fileName=""):
        self.isFile = isFile
        self.fileNameIdx = fileNameIdx
        if isFile:
            self.beginDataOffset = o4
            self.dataSize = o8
        else:
            self.parentDirIdx = o4
            self.nextNodeIdx = o8
        self.fileName = fileName

def selectFile():
    inp = 1
    while inp!=0:
        inp = int(input("Select Node: "))
        print(nodesList[inp].beginDataOffset)
        print(nodesList[inp].beginDataOffset+nodesList[inp].dataSize)
        #WiiFile.BRLYTFile(byteFile[nodesList[inp].beginDataOffset:nodesList[inp].beginDataOffset+nodesList[inp].dataSize])
        nsmbw.readDef(byteFile[nodesList[inp].beginDataOffset:nodesList[inp].beginDataOffset+nodesList[inp].dataSize])


def errMsgFilevaild(msg):
    print("Not a valid ARC file: " + msg)
    exit(0)

##################################################
##### ARC FILE HANDLING #####

def checkFileDir(byteFile,pos,isRoot=False):
    ### CHECK IS FILE/DIR ###
    typeCheckDigit = byteFile[pos]
    print("Node is file?",typeCheckDigit==0)
    if typeCheckDigit==0:
        #FILE HANDLING
        fileHandle(byteFile,pos)
    elif typeCheckDigit==1:
        #DIRECTORY HANDLING
        dirHandle(byteFile,pos,isRoot)
    else:
        errMsgFilevaild("Archive did not recognize any folders or files")
    print("===============")

def fileHandle(byteFile,offset):
    fileNameIdx = int.from_bytes(byteFile[offset+1:offset+4],"big")
    print("File Name offset index:",fileNameIdx)
    beginDataOffset = int.from_bytes(byteFile[offset+4:offset+8],"big")
    print("Offset to the start of the data:",beginDataOffset)
    dataSize = int.from_bytes(byteFile[offset+8:offset+12],"big")
    print("Size of this file:",dataSize)
    nodesList.append(U8Arc(True,fileNameIdx,beginDataOffset,dataSize))


def dirHandle(byteFile,offset,isRoot=False):
    global pointer
    pointer = offset+3
    if not isRoot:
        #Get the name
        #Note that root does not have name
        fileNameIdx = int.from_bytes(byteFile[offset+1:offset+4],"big")
        print("File Name offset index:",fileNameIdx)
    else:
        fileNameIdx = -1
    
    # Get the parent index
    # Returns 0 if the dir is at root
    pointer = offset+7
    parentDirIdx = int.from_bytes(byteFile[offset+4:offset+8],"big")
    print("Parent Index:",parentDirIdx)
    if not isRoot:
        #Get the next file in node
        pointer = offset+11
        nextNodeIdx = int.from_bytes(byteFile[offset+8:offset+12],"big")
        print("Next node Index:",nextNodeIdx)
        #Store the propereties
        nodesList.append(U8Arc(False,fileNameIdx,parentDirIdx,nextNodeIdx))
    else:
        #Get the total number of entries included (Directory/files)
        pointer = offset+11
        nodeTot = int.from_bytes(byteFile[offset+8:offset+12],"big")
        print("Total number of nodes:",nodeTot)
        # For Root: loop through each dir/files
        # (Each nodes are placed next to each other, forming an array/list)
        print("Loading sub-directories...")
        for i in range(1,nodeTot):
            print("NODE",i)
            pointer = pointer+12
            checkFileDir(byteFile,offset+(12*i))
        #i = nodeTot*12
        print("Start of the list of names")
        print("Current position/offset:",pointer)
        strNameOffset = pointer
        startOfStr = strNameOffset+nodesList[0].fileNameIdx
        endOfStr = offsetFirstNode+sizeAllNodes
        fNames_ = Util.binToUtf(byteFile[startOfStr:endOfStr])
        fNames = list(filter(None,"".join(list(map(Util.convertNULL,fNames_))).split(" ")))
        # Note: due to decode() does not return the NULL value, custom method is used

        print("File name list:",fNames)
        for i in range(1,len(nodesList)):
            nodesList[i].fileName = fNames[i]
            print("Named node",i,":",nodesList[i].fileName)

        selectFile()

def openFile(ARCfileName):
    ### OPEN FILE ###
    bfile = open(ARCfileName,"rb")
    byteFile = bfile.read()
    bfile.close()
    #print(chr(byteFile[0]))

    ### CHECK HEADER TEXT ###
    pointer = 3
    headerHex = byteFile[0:pointer+1].hex() #pointer+1 = 4
    if str(headerHex)!="55aa382d":
        errMsgFilevaild("Header not 'Uª8-'")

    ### CHECK OFFSET TO FIRST NODE ###
    pointer = 7
    offsetFirstNode = int.from_bytes(byteFile[4:pointer+1],"big")
    print("First(Root) node pos:",offsetFirstNode)

    ### CHECK SIZE OF ALL NODES ###
    pointer = 11
    sizeAllNodes = int.from_bytes(byteFile[8:pointer+1],"big")
    print("Size of all nodes:",sizeAllNodes)

    ### CHECK OFFSET OF FILE DATA ###
    pointer = 15
    offsetFileData = int.from_bytes(byteFile[12:pointer+1],"big")
    print("Start of file data:",offsetFileData)


    ### FILE/DIR HANDLING ###
    pointer = offsetFirstNode
    print("===============")
    checkFileDir(byteFile,offsetFirstNode,True)

openFile(ARCfileName)