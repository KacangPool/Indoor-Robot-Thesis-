#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Offline checks; no ROS, camera, model or network access required."""
import unittest
import person_detection_filter as subject


class Box(object):
    def __init__(self, label='person', score=0.9):
        self.Class = label
        self.probability = score
        self.id = 0
        self.xmin, self.ymin, self.xmax, self.ymax = 10, 20, 100, 200


class Message(object):
    def __init__(self):
        self.header = object()
        self.image_header = object()
        self.bounding_boxes = []


class Tests(unittest.TestCase):
    def test_person_only(self):
        person = Box()
        self.assertEqual(subject.select_person_boxes([Box('chair'), person, Box('traffic light')], 0.5), [person])

    def test_cutoff_inclusive(self):
        boundary = Box(score=0.5)
        self.assertEqual(subject.select_person_boxes([Box(score=0.499), boundary], 0.5), [boundary])

    def test_invalid_scores(self):
        values = [float('nan'), float('inf'), float('-inf'), None, 'invalid', -0.1, 1.1]
        self.assertEqual(subject.select_person_boxes([Box(score=x) for x in values], 0.5), [])

    def test_source_and_headers_preserved(self):
        source = Message()
        person = Box()
        original_boxes = [Box('chair'), person]
        source.bounding_boxes = original_boxes
        result = subject.filtered_message(source, Message, 0.5)
        self.assertIsNot(result, source)
        self.assertIs(result.header, source.header)
        self.assertIs(result.image_header, source.image_header)
        self.assertIs(source.bounding_boxes, original_boxes)
        self.assertEqual(len(source.bounding_boxes), 2)
        self.assertEqual(result.bounding_boxes, [person])
        self.assertEqual((person.id, person.xmin, person.ymin, person.xmax, person.ymax), (0, 10, 20, 100, 200))

    def test_empty_result_explicit(self):
        source = Message()
        source.bounding_boxes = [Box('chair')]
        self.assertEqual(subject.filtered_message(source, Message, 0.5).bounding_boxes, [])

    def test_defaults(self):
        args = subject.parse_args([])
        self.assertEqual((args.threshold, args.input_topic, args.output_topic),
                         (0.5, '/darknet_ros/bounding_boxes', '/fahad/person_boxes'))

    def test_output_preserves_vendor_namespace(self):
        with self.assertRaises(SystemExit):
            subject.parse_args(['--output-topic', '/darknet_ros/bounding_boxes'])

    def test_no_feedback_loop(self):
        with self.assertRaises(SystemExit):
            subject.parse_args(['--input-topic', '/fahad/person_boxes'])

    def test_invalid_cutoff(self):
        for value in ['nan', 'inf', '-0.1', '1.1']:
            with self.assertRaises(SystemExit):
                subject.parse_args(['--threshold', value])


if __name__ == '__main__':
    unittest.main()
