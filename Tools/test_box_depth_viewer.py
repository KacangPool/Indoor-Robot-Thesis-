#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Offline numerical/metadata checks. No ROS, GUI or hardware required."""
import unittest
import numpy as np
import box_depth_viewer as subject


class Tests(unittest.TestCase):
    def test_float_metres(self):
        raw = np.array([[1.25]], dtype=np.float32)
        self.assertAlmostEqual(subject.depth_metres(raw, '32FC1')[0, 0], 1.25)
        self.assertAlmostEqual(raw[0, 0], 1.25)

    def test_integer_millimetres(self):
        self.assertAlmostEqual(subject.depth_metres(np.array([[1250]], dtype=np.uint16), '16UC1')[0, 0], 1.25)

    def test_unsupported_encoding_and_channels(self):
        with self.assertRaises(ValueError):
            subject.depth_metres(np.ones((2, 2)), 'mono16')
        with self.assertRaises(ValueError):
            subject.depth_metres(np.ones((2, 2, 3)), '32FC1')

    def test_local_patch_not_whole_scene(self):
        depths = np.full((20, 20), 9.78, dtype=np.float32)
        depths[5:16, 5:16] = 1.0
        result = subject.patch_stats(depths, 10, 10)
        self.assertEqual(result['median'], 1.0)
        self.assertEqual((result['count'], result['total']), (121, 121))
        self.assertEqual(result['in_range_percent'], 100.0)

    def test_invalids_without_comparison_warning(self):
        depths = np.array([[np.nan, np.inf, -np.inf], [0, -1, 1], [2, 9.78, np.nan]], dtype=np.float32)
        with np.errstate(invalid='raise'):
            result = subject.patch_stats(depths, 1, 1, 1)
        self.assertEqual(result['count'], 3)
        self.assertAlmostEqual(result['valid_percent'], 100.0/3)
        self.assertAlmostEqual(result['in_range_percent'], 200.0/9)
        self.assertEqual(result['median'], 2.0)

    def test_out_of_range_not_hidden(self):
        result = subject.patch_stats(np.full((11, 11), 9.78), 5, 5)
        self.assertEqual(result['valid_percent'], 100.0)
        self.assertEqual(result['in_range_percent'], 0.0)
        self.assertAlmostEqual(result['median'], 9.78)

    def test_empty_numeric_patch(self):
        result = subject.patch_stats(np.zeros((5, 5)), 2, 2)
        self.assertEqual(result['count'], 0)
        self.assertIsNone(result['median'])

    def test_edge_clipping_and_point_sample(self):
        depths = np.ones((10, 10))
        self.assertEqual(subject.patch_stats(depths, 0, 0)['total'], 36)
        self.assertEqual(subject.patch_stats(depths, 0, 0, 0)['total'], 1)
        with self.assertRaises(ValueError):
            subject.patch_stats(depths, 10, 5)

    def problem(self, **changes):
        args = dict(rgb_shape=(480, 640, 3), depth_shape=(480, 640),
                    rgb_stamp=100.0, depth_stamp=100.02, rgb_frame='rgb_optical',
                    depth_frame='rgb_optical', max_delta=0.05, now_stamp=100.03)
        args.update(changes)
        return subject.pair_problem(**args)

    def test_acceptable_pair(self):
        self.assertIsNone(self.problem())

    def test_bad_geometry(self):
        self.assertIsNotNone(self.problem(depth_shape=(240, 320)))
        self.assertIsNotNone(self.problem(depth_frame='depth_optical'))
        self.assertIsNotNone(self.problem(rgb_frame='', depth_frame=''))

    def test_bad_pair_timestamps(self):
        self.assertIsNotNone(self.problem(depth_stamp=100.2))
        self.assertIsNotNone(self.problem(rgb_stamp=0))
        self.assertIsNotNone(self.problem(rgb_stamp=float('nan')))

    def test_old_and_future_acquisition(self):
        self.assertIsNotNone(self.problem(now_stamp=102.0))
        self.assertIsNotNone(self.problem(now_stamp=99.0))

    def test_cli_defaults(self):
        args = subject.parse_args([])
        self.assertEqual(args.radius, 5)
        self.assertEqual(args.depth_topic, '/camera/depth_registered/image_raw')


if __name__ == '__main__':
    unittest.main()
