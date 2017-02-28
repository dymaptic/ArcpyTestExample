import arcpy
from os.path import join


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
        self.label = "Toolbox"
        self.alias = "simple"

        # List of tool classes associated with this toolbox
        self.tools = [SimpleTool]


class SimpleTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "SimpleTool"
        self.description = "A simple tool to test"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = list()
        point_input = arcpy.Parameter(displayName="Point Features to Count",
                                      name="point_input",
                                      datatype="GPFeatureLayer",
                                      parameterType="Required",
                                      direction="Input")
        point_input.filter.list = ["Point"]
        params.append(point_input)

        intersect_polygons = arcpy.Parameter(displayName="Polygons to Intersect With",
                                             name="intersect_polygons",
                                             datatype="GPFeatureLayer",
                                             parameterType="Required",
                                             direction="Input")
        intersect_polygons.filter.list = ["Polygon"]
        params.append(intersect_polygons)

        output_polygons = arcpy.Parameter(displayName="Output Polygons",
                                          name="output_polygons",
                                          datatype="DEFeatureClass",
                                          parameterType="Required",
                                          direction="Output")
        output_polygons.parameterDependencies = [intersect_polygons.name]
        output_polygons.schema.clone = True

        red_count_field = arcpy.Field()
        red_count_field.aliasName = "Red Count"
        red_count_field.name = "Red_Count"
        red_count_field.type = "Integer"

        blue_count_field = arcpy.Field()
        blue_count_field.aliasName = "Blue Count"
        blue_count_field.name = "Blue_Count"
        blue_count_field.type = "Integer"

        output_polygons.schema.additionalFields = [red_count_field, blue_count_field]

        params.append(output_polygons)

        return params

    def get_parameter_by_name(self, parameters, name):
        try:
            return [p for p in parameters if p.name == name][0]
        except:
            raise KeyError("Parameter with name {} not found".format(name))

    def get_error_message_for_point_type_field(self, points):
        if points.Value:
            # verify that points has a "Type" field
            data = [f for f in arcpy.ListFields(points.Value) if f.name.upper() == 'TYPE']
            if (len(data)) == 0:
                return "{} does not contain a string field called TYPE".format(points.displayName)
        return None

    # def updateMessages(self, parameters):
    #     points = self.get_parameter_by_name(parameters, "point_input")
    #     if points.Value:
    #         # verify that points has a "Type" field
    #         data = [f for f in arcpy.ListFields(points.Value) if f.name.upper() == 'TYPE']
    #         if (len(data)) == 0 and not points.hasError():
    #             points.setErrorMessage("{} does not contain a string field called TYPE".format(points.displayName))

    # def updateMessages(self, parameters):
    #     points = self.get_parameter_by_name(parameters, "point_input")
    #     if points.Value:
    #         # verify that points has a "Type" field
    #         data = [f for f in arcpy.ListFields(points.Value) if f.name.upper() == 'TYPE']
    #         if (len(data)) == 0:
    #             points.setErrorMessage("{} does not contain a string field called TYPE".format(points.displayName))

    def execute(self, parameters, messages):
        """The source code of the tool."""
        points = self.get_parameter_by_name(parameters, "point_input")
        polygons = self.get_parameter_by_name(parameters, "intersect_polygons")
        output = self.get_parameter_by_name(parameters, "output_polygons")

        # Create a polygon layer that has the count of red points in "red_count"
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

        # Create a polygon layer that has the count of blue points in "blue_count"
        arcpy.MakeFeatureLayer_management(points.Value, "blue_points", "Type='{}'".format("BLUE"))
        polygon_blue_count = join("%scratchGDB%", "blue_count")
        arcpy.SpatialJoin_analysis(polygons.Value,
                                   "blue_points",
                                   polygon_blue_count,
                                   "JOIN_ONE_TO_ONE",
                                   "KEEP_ALL",
                                   None,
                                   "INTERSECT")
        arcpy.AlterField_management(polygon_blue_count, "Join_Count", "Blue_Count", "Blue Count")

        # Copy the original polygons to the output
        arcpy.CopyFeatures_management(polygons.Value, output.Value)

        # Use join field to move the red_count and blue_count fields
        arcpy.JoinField_management(output.Value, "OBJECTID", polygon_red_count, "TARGET_FID", "Red_Count")
        arcpy.JoinField_management(output.Value, "OBJECTID", polygon_blue_count, "TARGET_FID", "Blue_Count")
        return
