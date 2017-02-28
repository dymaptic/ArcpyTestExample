import arcpy
import os
import random
import string
import tempfile
import unittest
import arcgisscripting
from os import path


def get_temp_name():
    """
    Creates a random string that is a safe table or feature class name
    :return:
    """
    return ''.join([random.choice(string.ascii_uppercase) for _ in range(6)])


class FeatureClassAssertMixin(object):
    """
    Mixin for supporting the compare or assertion of two feature classes.
    """

    def assertFeatureClassEqual(self,
                                first,
                                second,
                                sort_field,
                                message=None,
                                compare_type=None,
                                ignore_options=None,
                                xy_tolerance=None,
                                m_tolerance=None,
                                z_tolerance=None,
                                attribute_tolerances=None,
                                omit_field=None):
        """
        Compares the second feature class to the first, and reports any issues.  Detailed issues are printed to the
        console if found.
        :param first:
        :param second:
        :param sort_field:
        :param message:
        :param compare_type:
        :param ignore_options:
        :param xy_tolerance:
        :param m_tolerance:
        :param z_tolerance:
        :param attribute_tolerances:
        :param omit_field:
        :return:
        """

        # Make a place to store the compare file
        compare_file = tempfile.mkstemp(".txt")
        os.close(compare_file[0])
        result = arcpy.FeatureCompare_management(first,
                                                 second,
                                                 sort_field,
                                                 compare_type,
                                                 ignore_options,
                                                 xy_tolerance,
                                                 m_tolerance,
                                                 z_tolerance,
                                                 attribute_tolerances,
                                                 omit_field,
                                                 continue_compare=True,
                                                 out_compare_file=compare_file[1])
        if 'true' == result.getOutput(1):
            # delete the compare file
            os.remove(compare_file[1])
            return

        # read the compare file and print it out
        print(compare_file[1])
        with open(compare_file[1]) as f:
            [print(l.rstrip()) for l in f.readlines()]
        os.remove(compare_file[1])

        # set the assertion message.
        msg = message if message is not None else "Feature class {} is not equal to {}".format(second, first)
        raise AssertionError(msg)


class SimpleToolboxTests(unittest.TestCase, FeatureClassAssertMixin):

    def setUp(self):
        arcpy.env.overwriteOutput = True
        self.parent_directory = path.dirname(path.expandvars(__file__))
        self.data_directory = path.join(self.parent_directory, "data")
        arcpy.AddToolbox(path.join(path.dirname(self.parent_directory), "SimpleToolbox.pyt"))

    def test_single_polygon_red(self):
        """
        A single polygon with three red points.
        :return:
        """
        # Setup
        points = path.join(self.data_directory, "single_polygon_red.gdb", "points")
        polygons = path.join(self.data_directory, "single_polygon_red.gdb", "polygons")
        answer = path.join(self.data_directory, "single_polygon_red.gdb", "answer")
        output = path.join("%ScratchGDB%", get_temp_name())
        # Run
        arcpy.SimpleTool_simple(points, polygons, output)
        # assert
        self.assertFeatureClassEqual(answer, output, "OBJECTID")
        # cleanup
        arcpy.Delete_management(output)

    def test_single_polygon_blue(self):
        """
        A single polygon with three blue points.
        :return:
        """
        # Setup
        points = path.join(self.data_directory, "single_polygon_blue.gdb", "points")
        polygons = path.join(self.data_directory, "single_polygon_blue.gdb", "polygons")
        answer = path.join(self.data_directory, "single_polygon_blue.gdb", "answer")
        output = path.join("%ScratchGDB%", get_temp_name())
        # Run
        arcpy.SimpleTool_simple(points, polygons, output)
        # assert
        self.assertFeatureClassEqual(answer, output, "OBJECTID")
        # cleanup
        arcpy.Delete_management(output)

    def test_single_polygon_no_points(self):
        """
        A single polygon with no points in the points layer (empty, no records)
        :return:
        """
        # Setup
        points = path.join(self.data_directory, "single_polygon_no_points.gdb", "points")
        polygons = path.join(self.data_directory, "single_polygon_no_points.gdb", "polygons")
        answer = path.join(self.data_directory, "single_polygon_no_points.gdb", "answer")
        output = path.join("%ScratchGDB%", get_temp_name())
        # Run
        arcpy.SimpleTool_simple(points, polygons, output)
        # assert
        self.assertFeatureClassEqual(answer, output, "OBJECTID")
        # cleanup
        arcpy.Delete_management(output)

    def test_single_polygon_no_points_by_filter(self):
        """
        A single polygon with no points in the points layer that match either BLUE or RED, but there are ORANGE ones.
        :return:
        """
        # Setup
        points = path.join(self.data_directory, "single_polygon_no_points_by_filter.gdb", "points")
        polygons = path.join(self.data_directory, "single_polygon_no_points_by_filter.gdb", "polygons")
        answer = path.join(self.data_directory, "single_polygon_no_points_by_filter.gdb", "answer")
        output = path.join("%ScratchGDB%", get_temp_name())
        # Run
        arcpy.SimpleTool_simple(points, polygons, output)
        # assert
        self.assertFeatureClassEqual(answer, output, "OBJECTID")
        # cleanup
        arcpy.Delete_management(output)

    def test_random_data_01(self):
        """
        A 10x10 grid with 100 random points.
        :return:
        """
        # Setup
        points = path.join(self.data_directory, "random_data_01.gdb", "points")
        polygons = path.join(self.data_directory, "random_data_01.gdb", "polygons")
        answer = path.join(self.data_directory, "random_data_01.gdb", "answer")
        output = path.join("%ScratchGDB%", get_temp_name())
        # Run
        arcpy.SimpleTool_simple(points, polygons, output)
        # assert
        self.assertFeatureClassEqual(answer, output, "OBJECTID")
        # cleanup
        arcpy.Delete_management(output)

    def test_invalid_point_data(self):
        """
        Passes a polygon in to the point layer.
        :return:
        """
        # Setup
        points = path.join(self.data_directory, "random_data_01.gdb", "polygons")
        polygons = path.join(self.data_directory, "random_data_01.gdb", "polygons")
        output = path.join("%ScratchGDB%", get_temp_name())
        # Run with assert exception raised
        with self.assertRaisesRegex(arcgisscripting.ExecuteError, 'Invalid geometry type'):
            arcpy.SimpleTool_simple(points, polygons, output)

    def test_invalid_polygon_data(self):
        """
        Passes a point in to the polygon layer.
        :return:
        """
        # Setup
        points = path.join(self.data_directory, "random_data_01.gdb", "points")
        polygons = path.join(self.data_directory, "random_data_01.gdb", "points")
        output = path.join("%ScratchGDB%", get_temp_name())
        # Run with assert exception raised
        with self.assertRaisesRegex(arcgisscripting.ExecuteError, 'Invalid geometry type'):
            arcpy.SimpleTool_simple(points, polygons, output)

    # def test_invalid_point_layer_missing_type_field(self):
    #     """
    #     Passes a point layer that is missing the type field.
    #     :return:
    #     """
    #     # Setup
    #     points = path.join(self.data_directory, "point_layer_no_type_field.gdb", "points")
    #     polygons = path.join(self.data_directory, "point_layer_no_type_field.gdb", "polygons")
    #     output = path.join("%ScratchGDB%", get_temp_name())
    #     # Run with assert exception raised
    #     with self.assertRaisesRegex(arcgisscripting.ExecuteError, 'does not contain a string field called TYPE'):
    #         arcpy.SimpleTool_simple(points, polygons, output)

if __name__ == '__main__':
    unittest.main()
