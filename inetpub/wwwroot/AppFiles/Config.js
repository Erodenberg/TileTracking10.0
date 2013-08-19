// config settings for the Descriptive Tile Analysis application
// change the service URLs and other properties to work with your GIS server.

function setConfigProperties(){
	
	//****** You will need to change items in this section to work with your data

		//Application Title
	//Change this value to update the application Title
	appTitle = "ArcGIS Server: Delco Basemap Tile Usage Hotmap";
	
	var server = checkVal("http://oheric2.stl.esri.com/ArcGIS/rest/services/")  // url for server rest services directory, ends with "/"
	
	tilelevelStr = server + "Delaware/CacheUsageHeatmap/MapServer/1"; 											   //Feature Layer Service list of available tile levels to choose from
	tiletrackingStr = server + "Delaware/CacheUsageHeatmap/MapServer/0";                                           //Feature Layer Service providing Tile Hits
	
	// WGS 84 Web Mercator with Auxillary Sphere
	spRef = new esri.SpatialReference({ wkid: 3857 });
	
	// This is the initial extent for Delaware County, Ohio.  Change numerical values to reflect your initial extent.
	startExtent = new esri.geometry.Extent(-9305707.93779248, 4868488.35515, -9166370.06570752, 4954587.02385, spRef);
	
	// Scale Level field name
	// the name of the field can be found in the rest end point of 
	// the Feature Layer Service storing the list of available scale levels.
	levelField = "LevelID"
	
	// Class Break Renderer Attribute Field to symbolize by
	breakField = "TileTracking.DBO.TileHit_Frequency.FREQUENCY";
	
	// Info Window Content
	// Change the field names contained in the 
	// Curly Braces to reflect your field names {Your Field.Name}
	infoContent = "<b>Tile ID: ${TileTracking.DBO.DelCoBaseMapTilingScheme.TileID}</b><hr>" +
	 "<b>Scale Level</b>: ${TileTracking.DBO.DelCoBaseMapTilingScheme.LevelID}" +
	 "<br><b>Row</b>: ${TileTracking.DBO.DelCoBaseMapTilingScheme.RowID}" +  
	 "<br><b>Column</b>: ${TileTracking.DBO.DelCoBaseMapTilingScheme.ColumnID}" +
	 "<br><b>Number of Hits</b>: ${TileTracking.DBO.TileHit_Frequency.FREQUENCY}";
			
	//Renderer Definition Query
	//Definition query fields come from the tiletrackingStr Service.  Search the rest endpoint of 
	//this server and locate the fields FREQUENCY and TileID
	defExpression = "TileTracking.DBO.TileHit_Frequency.FREQUENCY > 0 AND TileTracking.DBO.DelCoBaseMapTilingScheme.LevelID = ";
	
	
	//**********This Section is purely for the aesthetics of the application and is not required to be changed**********
	
	streetmapService  = "http://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer";          //Service providing the application Basemap... ArcGIS Online World Streetmap
	
	// Legend Text
	classBreak1 = "1 - 9 hits";
	classBreak2 = "10 - 100 hits";
	classBreak3 = "100+ hits";
	
	// Legend Symbology
	// [Red, Green, Blue, Transparency]
	classSymbol1 = [255,255,0,0.50];    // yellow
	classSymbol2 = [255, 170, 0, 0.5];	// orange
	classSymbol3 = [255, 0, 0, 0.5];	// red
	
	// Legend Patch Size
	patchSize = 25;
	
	// Legend Title
	// Enter the Name you want to appear in the legend title
	legendTitle = "Tile Usage";
	
	// Class Break Renderer Break Points
	// Renderer consists of 3 breaks.  More can be added to the TileUsage.html.  Search for 
	// the function initOperationalLayer to add more breaks.  Then add break min and max values
	// below.  Also add break color schemes.
    // If you have ESRI's ArcMap available, this can be a good way to determine break values.
    // You can also copy the RGB values from the color schemes ArcMap applies, or use colors
    // from a site like www.colorbrewer.org
	break1Min = 1;
	break1Max = 9;
	break2Min = 10;
	break2Max = 99;
	break3Min = 100;
	break3Max = Infinity;
	
	//[Red, Green, Blue, Transparency]
	break1Sym = [255,255,0,0.50];       // yellow
	break2Sym = [255, 170, 0, 0.5];	    // orange
	break3Sym = [255, 0, 0, 0.5];		// red

}

//****************Do not modify beyond this point**************

function checkVal(strUrl){
	// check that the server URL paths end with a "/", add it if not present
	var strLen = strUrl.length;
	if (strUrl.substring(strLen - 1, strLen) != "/") {
		alert(strUrl + " in config.js is missing '/' at the end of the string, automatically added");
		strUrl = strUrl + "/";
	}
	return (strUrl);
}