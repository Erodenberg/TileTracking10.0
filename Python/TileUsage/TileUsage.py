# ---------------------------------------------------------------------------
## Name:            TileUsage.py
## 
## Purpose:         This script imports the IISLogsLP SQL database and adds four 
##                  fields named Scale Level, Row and Column and TileID.  Once the fields are
##                  are calculated a frequency analysis is run on the TileID field to determine how
##                  many hits each tile in the map cache has been viewed.
## 
## Author:          Eric J. Rodenberg, Esri
## 
## Date:            Wednesday, July 28, 2010 
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
# Import arcpy module
import arcpy, sys, traceback
from arcpy import env

env.overwriteoutput = 1
#*******************  Edit the locations of the SQL Server Database Connection and Tile Scheme Geodatabase***************************
dbo_IISLogsLP = "D:/Projects/ags_Server/Caching/TileTracking/DataConnections/SQL@NativeConnection@IISLogsLP.odc/dbo.IISLogsLP"
TilingScheme_gdb = "D:/Projects/ags_Server/Caching/TileTracking/DataConnections/DC@oheric2@TileTracking.sde"
tileHits = 'TileTracking.DBO.IIS_TileHits'
Frequency = 'TileTracking.DBO.TileHit_Frequency'
#Do Not Edit Below This Comment
FrequencyField = ["TileID"]

env.worksapce = TilingScheme_gdb

#Delete the IIS_TableHits and reload it into the Geodatabase
if arcpy.Exists(TilingScheme_gdb + '/' + tileHits):
    arcpy.Delete_management(TilingScheme_gdb + '/' + tileHits)

if arcpy.Exists(TilingScheme_gdb + '/' + Frequency):
    arcpy.Delete_management(TilingScheme_gdb + '/' + Frequency)

try:
    #Process: Table to Table
    arcpy.TableToTable_conversion(dbo_IISLogsLP, TilingScheme_gdb, tileHits)
        
    # Process: Add LevelID
    arcpy.AddField_management(TilingScheme_gdb + '/' + tileHits, "LevelID", "TEXT", "", "", "2", "", "NULLABLE", "NON_REQUIRED", "")
    
    # Process: Add RowID
    arcpy.AddField_management(TilingScheme_gdb + '/' + tileHits, "RowID", "TEXT", "", "", "15", "", "NULLABLE", "NON_REQUIRED", "")
    
    # Process: Add ColumnID
    arcpy.AddField_management(TilingScheme_gdb + '/' + tileHits, "ColumnID", "TEXT", "", "", "15", "", "NULLABLE", "NON_REQUIRED", "")
    
    # Process: Add TileID
    arcpy.AddField_management(TilingScheme_gdb + '/' + tileHits, "TileID", "TEXT", "", "", "25", "", "NULLABLE", "NON_REQUIRED", "")
    
    rows = arcpy.UpdateCursor(TilingScheme_gdb + '/' + tileHits)
    
    arcpy.AddMessage("Updating Level, Row and Column Information")
    for row in rows:
        currentURL = row.csUriStem
        levRowCol = currentURL.split("/")
        theList = levRowCol[-3:]
        row.LevelID = theList[0]
        row.RowID = theList[1]
        row.ColumnID = theList[2]
        row.TileID = theList[0] + theList[1] + theList[2]
        rows.updateRow(row)            
    del row
    del rows
        
    currentURL = ""
    
    arcpy.Frequency_analysis(TilingScheme_gdb + '/' + tileHits, TilingScheme_gdb + '/' + Frequency, FrequencyField, "" )
    arcpy.AddIndex_management(TilingScheme_gdb + '/' + Frequency,"TileID","TileHit_Index","UNIQUE","NON_ASCENDING")
    arcpy.AddMessage("Done!")
    
except:
    # Get the traceback object
    #
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    # Concatenate information together concerning the error into a 
    #   message string
    #
    pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)
    # Return python error messages for use with a script tool
    #
    arcpy.AddError(pymsg)
    # Print Python error messages for use in Python/PythonWin
    #
    print pymsg
    
        