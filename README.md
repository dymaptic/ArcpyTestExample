# ArcpyTestExample
Source code for my presentation at the 2017 dev summit on unit tests for ArcToolbox Tools

This project provides a simple toolbox tool written as a PYT and a set of tests and corresponding test data used to 
demonstrate how to build tests for toolbox tools.

## The Tool

A simple tool that meets the following requirements:

1) Input - Points with a "Type" field either "RED" or "BLUE"
2) Input - Polygons
3) Output - A copy of the Polygon input with  "Red_Count" and "Blue_Count" fields that contain the number of "RED" 
points and the number of "BLUE" points in that polygon.

This is achieved by the following process:

1) Filter the input points using a feature layer and where clause
2) Use a spatial join to join the polygons and filtered points into a new temporary layer
3) Alter the field name "Join_Count" (provided by SpatialJoin) to have the correct name either "Red_Count" or 
"Blue_Count"

````python
arcpy.MakeFeatureLayer_management(points.Value, "red_points", "Type='{}'".format("RED"))
polygon_red_count = join("%scratchGDB%", "red_count")
arcpy.SpatialJoin_analysis(polygons.Value,
                           "red_points",
                           polygon_red_count,
                           "JOIN_ONE_TO_ONE",
                           "KEEP_ALL",
                           None,
                           "INTERSECT")
arcpy.AlterField_management(polygon_red_count, "Join_Count", "Red_Count", "Red Count")
````
## The Tests

The process above provides a simple process to test, as a result the tests can be simple as well.  The tests and 
categories provided in this file are:

1) Edge Cases
    1) All Blue Points
    1) All Red Points
    1) No Points
    1) No Points, but there are points of other "types"
1) General Data - A random set of points in a grid.  A substitute for building tests on real data.
1) Exceptions
    1) Passing polygons into the point input
    1) Passing points into the polygon input
    1) No Type field