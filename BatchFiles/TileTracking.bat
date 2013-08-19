Rem Stop Tileusage Service so that the IIS Logs can be refreshed with the previous days activities
cd /D "D:\Projects\ags_Server\Caching\TileTracking\AGSSOMv10.0"
AGSSOM.exe -x delaware/CacheUsageHeatmap

Rem Update IISLogsLP with the previous days activites
cd /D "C:\Program Files\Log Parser 2.2"
LogParser.exe "SELECT TO_TIMESTAMP(date, time) AS dateTime, c-ip, time-taken, cs-uri-stem FROM c:\inetpub\logs\LogFiles\w3svc1\u_extend1.log TO IISLogsLP WHERE cs-uri-stem LIKE '/ArcGIS/rest/services/Delaware/DelCoBaseMap/MapServer/tile%%' AND dateTime >= SUB(SYSTEM_TIMESTAMP(), TIMESTAMP('0000-01-01 23:59:59','yyyy-mm-dd hh:mm:ss'))" -o:SQL -oConnString: "Driver={SQL Server Native Client 10.0}; Server=.\sqlexpress; Database=IISLogsLP;Trusted_Connection=yes;" -ignoreMinwarns:OFF -createTable:ON -maxStrFieldLen:8000

Rem Update Tileusage Geodatabase
echo on
C:\Python26\ArcGIS10.0\python.exe "D:\Projects\ags_Server\Caching\TileTracking\Python\TileUsage\TileUsage.py" 
echo off

Rem Restart Tile Usage Map Service
cd /D "D:\Projects\ags_Server\Caching\TileTracking\AGSSOMv10.0"
AGSSOM.exe -s delaware/CacheUsageHeatmap