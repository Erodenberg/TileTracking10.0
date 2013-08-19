## Name:            ServiceInfo.py
## 
## Purpose:         Reads an ArcGIS Server Cached Map Service REST end point and 
##                  extracts TileInfo, Columns, Rows Origin X, Origin Y and Full Extent
##                  using Urllib2 to get to the URL and JSON to interpret and read the 
##                  ArcGIS Server Java Script Object Notation.
## 
## Author:          Tom Brenneman, Esri
## 
## Date:            Thursday, September 10, 2009
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
import math

def getCacheInfo(URL, datasetExtent=''):
    import urllib2, json 
#    from StringIO import StringIO
    
    serviceURL = URL + "?f=json"
    req = urllib2.Request(url=serviceURL)
    f = urllib2.urlopen(req)
    jsonRespons = f.read()
    serviceInfo = json.loads(jsonRespons)
    
    tileInfo = serviceInfo['tileInfo']
    tilePixelHeigh = tileInfo['cols']
    tilePixelWidth = tileInfo['rows']
    tileOriginX = tileInfo['origin']['x']
    tileOriginY = tileInfo['origin']['y']
    fullExtent = serviceInfo['fullExtent']
    
    levels = {}
    for lod in tileInfo['lods']:
        res = lod['resolution']
        scale = lod['scale']
        tileGroundWidth = tilePixelWidth * res
        tileGroundHeight = tilePixelHeigh * res
        if datasetExtent != '':
            xMin = tileOriginX-datasetExtent.XMin
            yMin = tileOriginY-datasetExtent.YMin
            xMax = tileOriginX-datasetExtent.XMax
            yMax = tileOriginY-datasetExtent.YMax
        else:
            xMin = tileOriginX-fullExtent['xmin']
            yMin = tileOriginY-fullExtent['ymin']
            xMax = tileOriginX-fullExtent['xmax']
            yMax = tileOriginY-fullExtent['ymax']
        startTileRow = abs(math.trunc((yMax)/tileGroundHeight))
        endTileRow = abs(math.trunc((yMin)/tileGroundHeight))
        startTileCol = abs(math.trunc((xMin)/tileGroundWidth))
        endTileCol = abs(math.trunc((xMax)/tileGroundWidth))
        
        levels[lod['level']] = {'scale': scale, 'resolution': res, 
                                'tileGroundWidth': tileGroundWidth, 
                                'tileGroundHeight': tileGroundHeight,
                                'startTileRow': startTileRow,
                                'endTileRow': endTileRow,
                                'startTileCol': startTileCol,
                                'endTileCol': endTileCol}
    cacheInfo = {'spatialReference': tileInfo['spatialReference'], 'fullExtent': fullExtent, 'originX': tileOriginX,'originY': tileOriginY, 'tileHeight': tileInfo['cols'], 'tileWidth': tileInfo['rows'], 'levels': levels }
    return cacheInfo
