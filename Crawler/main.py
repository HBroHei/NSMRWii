import PIL
import globalVars
import Util

from copy import deepcopy

# Check if some of the randomised entrances are inaccessible
def checkForEntranceLoops(areaNo,entranceData):
    levelMap = generateTextLevelMap(areaNo)
    pathLevelMap = [[0 for x in range(levelMap[0].length)] for y in range(levelMap.length)]
    for _entPos in entranceData:
        entPos = Util.objPosToTilePos(_entPos)
        crawlerCurPos = [entPos[0],entPos[1]]
        crawlerPrevPos = deepcopy(crawlerCurPos)

        # Check if current tile is enterable entrance

        # Check if adjacent tile are enterable pipes (cehck entrance + tile ID)

        if [crawlerCurPos[1]-1]==0:
            crawlerCurPos[1] -= 1
    pass

def generateTextLevelMap(areaNo):
    max_x = max([d[1] + d[3] for d in globalVars.tilesData[areaNo]])
    max_y = max([d[2] + d[4] for d in globalVars.tilesData[areaNo]])

    # Initialize the grid with spaces
    grid = [[0 for _ in range(max_x)] for _ in range(max_y)]
    
    # Fill in the grid with the tiles
    for tile in globalVars.tilesData[j]:
        tile_id, x, y, w, h = tile
        for i2 in range(y, (y+h)):
            for j2 in range(x, (x+w)):
                digit = str(tile_id).zfill(4)  # Take the last two digits of the tile ID
                grid[i2][j2] = tile_id
    
    return grid