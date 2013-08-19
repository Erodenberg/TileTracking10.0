## Name:            CreateTilingSchemeFC.py
##
## Version          2.0
## 
## Purpose:         Creates a polygon feature class for each level of an exploded cache
##                  tiling schemes using the ArcGIS 10 ArcPy module. Additionally four 
##                  fields are created and populated to track the Scale Level, Row and Column and
##                  Tile ID. The TileID field concatenates the Scale Level, Row and Column fields
##                  into one unique ID. 
##
## Enhancements:    1. CreateTilingShceme now supports exploded or compact caches.
##                  2. Output Gedodatabase is now projected to match the spatial reference of the
##                     cache map service it represents.
##                  3. Output Geodatabase location can be determined by the end user.
##                  4. Extent feature class is used to determine the full extent of the tiling scheme.
## 
## Author:          Adapted from Tom Brenneman's Cache Validation tools
##                  Eric J. Rodenberg, Esri 
## 
## Date:            Wednesday, July 28, 2010
## Updated:         Friday, October 15, 2010
## 
## Version:         Python 2.6.5 (r265:79096, Mar 19 2010, 21:48:26) [MSC v.1500 32 bit (Intel)] on win32]
## 
## Copyright 2001-2010 ESRI. 
## All rights reserved under the copyright laws of the United States. 
## You may freely redistribute and use this sample code, with or without 
## modification. The sample code is provided without any technical support or 
## updates. 
## 
## Disclaimer OF Warranty: THE SAMPLE CODE IS PROVIDED "AS IS" AND ANY EXPRESS OR 
## IMPLIED WARRANTIES, INCLUDING THE IMPLIED WARRANTIES OF MERCHANTABILITY 
## FITNESS FOR A PARTICULAR PURPOSE, OR NONINFRINGEMENT ARE DISCLAIMED. IN NO 
## EVENT SHALL ESRI OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, 
## INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT 
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR 
## PROFITS; OR BUSINESS INTERRUPTION) SUSTAINED BY YOU OR A THIRD PARTY, HOWEVER 
## CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
## OR TORT ARISING IN ANY WAY OUT OF THE USE OF THIS SAMPLE CODE, EVEN IF ADVISED 
## OF THE POSSIBILITY OF SUCH DAMAGE. THESE LIMITATIONS SHALL APPLY 
## NOTWITHSTANDING ANY FAILURE OF ESSENTIAL PURPOSE OF ANY LIMITED REMEDY. 
## 
## For additional information contact: 
## 
## Environmental Systems Research Institute, Inc. 
## Attn: Contracts Dept. 
## 380 New York Street 
## Redlands, California, U.S.A. 92373 
## Email: contracts@esri.com 
##*********************************************************************** 

#Begin Script... 

#Add Arcpy and other modules 
import arcpy, sys, os, glob, serviceInfo, traceback, math, urllib2, copy
from arcpy import env

def getTileCoords(originX, originY, row, col, tileGroundHeight, tileGroundWidth):
    x = (originX + (col * tileGroundWidth))
    y = (originY - (row * tileGroundHeight)) - tileGroundHeight
    return [[x, y], [x + tileGroundWidth, y], [x + tileGroundWidth, y + tileGroundHeight],[x, y  + tileGroundHeight]]

def getOneDim(pntsCol, dim):
    dimCoord = []
    for coord in pntsCol:
        dimCoord.append(coord[dim])
    return dimCoord
        
def rangeWithLast(minVal, maxVal):
    return range(minVal, maxVal + 1)

def addTilePoly(cur, pntsCol, pntsarcpy, levelID, rowNum, colNum):
    xCoords = getOneDim(pntsCol, 0)
    yCoords = getOneDim(pntsCol, 1)
    maxX = max(xCoords)
    maxY = max(yCoords)
    minX = min(xCoords)
    minY = min(yCoords)
    
    for coord in [[minX, minY], [minX, maxY], [maxX, maxY], [maxX, minY]]:
        pnt = arcpy.Point(coord[0], coord[1])
        pntsarcpy.add(pnt)
    feat = cur.newRow()
    feat.shape = pntsarcpy
    feat.LevelID = str(levelID)
    feat.RowID = str(rowNum) 
    feat.ColumnID = str(colNum)
    feat.TileID = str(levelID) + str(rowNum)+ str(colNum)
    cur.insertRow(feat)
    pntsarcpy.removeAll()
    
def logMessage(message, logFile=''):
    arcpy.AddMessage(message)
    if logFile != '':
        logFile.write(message)

def usage():
    print "Usage CreateTilingSchemeFC.py <REST url to MapServer> <levels to process> <output Geodatabase location>\n\
    <Feature Class extent to model the cache from> \n\
    Example:\n\ CreateTilingSchemeFC.py \"http://localhost/ArcGIS/rest/services/myMap/MapServer\" 0,1,2,3,4\ \n\
    c:\temp\outputLocation\ c:\temp\outputLocation\myMapCacheExtent.shp" "Create Combined Feature Class True or False"
    sys.exit(1)

if __name__ == '__main__':
    try:
        if len(sys.argv) < 4:
            usage()
        try:
            cacheURL = sys.argv[1]
            levelsToProcess = sys.argv[2].split(',')
            outputGdbLocation = sys.argv[3]
            singleFC = sys.argv[4]
            inputExtentFC = arcpy.GetParameterAsText(4)
            
        except:
            usage()
            
        #Get cache service information
        cacheInfo = serviceInfo.getCacheInfo(cacheURL)
        path = os.path
        try:
            wkid = cacheInfo['spatialReference']['wkid']
            outputSR = arcpy.SpatialReference()
            outputSR.factoryCode = wkid
            outputSR.create()
        except:
            wkt = cacheInfo['spatialReference']['wkt']
            prjPath = path.join(outputGdbLocation, 'service.prj')
            prjFile = open(prjPath, 'w')
            prjFile.write(wkt)
            prjFile.close()
            outputSR = arcpy.SpatialReference(prjPath)
        env.outputCoordinateSystem = outputSR
        env.overwriteoutput = 1
        
        #Setup the output workspace
        fileGdb = path.join(outputGdbLocation,"TilingScheme.gdb")
        i = 0
        while arcpy.Exists(fileGdb):
            i += 1
            fileGdb = path.join(outputGdbLocation,"TilingScheme%0s.gdb" % i)            
        sFileGdbBase = path.basename(fileGdb)
        arcpy.CreateFileGDB_management(outputGdbLocation, sFileGdbBase, "CURRENT")
        env.workspace = fileGdb
        
        #Create the extent feature class in the same coordinate system as the map service
        extentFC = path.join(env.workspace, 'ValidationExtent')
        arcpy.CopyFeatures_management(inputExtentFC,extentFC)
        #Adjust the extent of the cache to analyze to the extent of the extent feature class
        cacheInfo = serviceInfo.getCacheInfo(cacheURL, arcpy.Describe(extentFC).extent)
        originX = cacheInfo['originX']
        originY = cacheInfo['originY']
        cacheLODs = cacheInfo['levels']
        
        dblTotalNumFiles = 0
        
        for cacheLevel in cacheInfo['levels']: #os.listdir(cacheFolder):
            if str(cacheLevel) not in levelsToProcess:
                logMessage("Skipping level %0s\n" % (cacheLevel))
                continue
            
            logMessage("Processing level %0i\n" % (cacheLevel))
            curLevel = cacheLODs[cacheLevel]
            tileGroundWidth = curLevel['tileGroundWidth']
            tileGroundHeight = curLevel['tileGroundHeight']
            
            outTilingSchemeFC = "level" + str(cacheLevel) + "_Scheme"
            arcpy.CreateFeatureclass_management(env.workspace, outTilingSchemeFC, "Polygon", "#", "#", "#", outputSR)
            
            inFeatures = outTilingSchemeFC
            fieldName = "LevelID"
            fieldLen = 2
            fieldName1 = "RowID"
            fieldLen1 = 10
            fieldName2 = "ColumnID"
            fieldLen2 = 10
            fieldName3 = "TileID"
            fieldLen3 = 25
            
            arcpy.AddField_management(inFeatures, fieldName, "Text", "", "", fieldLen)
            arcpy.AddField_management(inFeatures, fieldName1, "Text", "","", fieldLen1)
            arcpy.AddField_management(inFeatures, fieldName2, "Text", "","", fieldLen2)
            arcpy.AddField_management(inFeatures, fieldName3, "Text", "", "", fieldLen3)
            
            tiling_schemeCur = arcpy.InsertCursor(outTilingSchemeFC)
                       
            dblLevelSize = 0.0
            dblNumFiles = 0
            
            pnts = arcpy.Array()
            rows = rangeWithLast(curLevel['startTileRow'], curLevel['endTileRow'])
            columns = rangeWithLast(curLevel['startTileCol'], curLevel['endTileCol'])
            rowReportInc = math.ceil(len(rows) / 100.0)
            for rowIndx, cacheRow in enumerate(rows):
                rowTileCoords = []
                
                if (rowIndx + 1 ) % rowReportInc == 0:
                    logMessage("Processed %0i of %1i rows in level %2i\n" % (rowIndx + 1, len(rows), cacheLevel))
                    
                for cacheCol in columns:
                    #Calc some cache stats
                    dblNumFiles+=1 #Number of files
                    fullTileURL = cacheURL + "/tile/" + str(cacheLevel) + "/" + str(cacheRow) + "/" + str(cacheCol)
                    
                    try:
                        req = urllib2.Request(url=fullTileURL)
                        httpFile = urllib2.urlopen(req)
                        cacheTile = httpFile.read()
                    except:
                        continue
                    
                    dblFileSize = len(cacheTile) #path.getsize(cacheCol)
                    dblLevelSize+=dblFileSize #the total size of this level
                    
                    #Write the tile to the coverage feature class
                    tileCoords = getTileCoords(originX, originY, cacheRow, cacheCol, tileGroundHeight, tileGroundWidth)
                    
                    xCoords = []
                    for coord in tileCoords:
                        xCoords.append(coord[0])
                    
                    commonCoordsRowIndx = []
                    commonCoordsTileIndx = []
                    if len(rowTileCoords) == 0: #If this is the first tile in the row then row coords = tile coords
                        rowTileCoords = tileCoords
                    else:
                        cluster = 100000 #Cluster tolerance for determining coincidence
                        tileXCoords = getOneDim(tileCoords, 0)
                        rowXCoords = getOneDim(rowTileCoords, 0)
                        for xCoord in tileXCoords:
                            for rowXCoord in rowXCoords:
                                if  math.floor((xCoord * cluster)) == math.floor(rowXCoord * cluster):
                                    #Remove the row coordinates with this x coordinate
                                    tempCoords = []
                                    for v in rowTileCoords:
                                        if v[0] == rowXCoord:
                                            tempCoords.append(v)
                                    for v in tempCoords:
                                        rowTileCoords.remove(v)
                                    #remove the tile coordinates with this x coordinate
                                    tempCoords = []
                                    for v in tileCoords:
                                        if v[0] == xCoord:
                                            tempCoords.append(v)
                                    for v in tempCoords:
                                        tileCoords.remove(v)
                                    break
                            if len(rowTileCoords) == 2:
                                break
                        if len(rowTileCoords) == 2:
                            rowTileCoords += tileCoords
                        else: #This tile is not adjacent to the last
                            addTilePoly(tiling_schemeCur, schemeCoords, pnts, cacheLevel, cacheRow, cacheCol)
                            schemeCoords = tileCoords
                        schemeCoords = getTileCoords(originX, originY, cacheRow, cacheCol, tileGroundHeight, tileGroundWidth)                                    
                        addTilePoly(tiling_schemeCur, schemeCoords, pnts, cacheLevel, cacheRow, cacheCol)                    
            #Delete the cursors
            del tiling_schemeCur
                        
        arcpy.Delete_management(extentFC)
        
        if (singleFC != "false"):
            env.workspace = fileGdb
            fcList = arcpy.ListFeatureClasses()
            outFC = fileGdb + os.sep + 'CacheMapTilingScheme'
            arcpy.Merge_management(fcList, outFC)
        logMessage("Create Tiling Scheme Feature Classes has successfully completed.")
        
    except:
        # mail((fromAdd, toAdd), 'Cache validation error', 'Error during cache validation for ' + gisServer)
        logMessage("Error!")
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_info)
        try:
            logMessage(pymsg, f)
            logMessage(arcpy.GetMessages(2), f)
            f.close()
        except:
            logMessage(pymsg)
            logMessage(arcpy.GetMessages(2))