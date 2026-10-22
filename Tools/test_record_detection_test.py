"""Offline checks: python -m unittest discover -s Tools -p test_record_detection_test.py"""
from __future__ import print_function
import unittest
import io
import json
import record_detection_test as recorder


class Object(object):
    pass


def header(seq=1, secs=2, nsecs=3, frame='camera_rgb_optical_frame'):
    value = Object()
    value.seq = seq
    value.stamp = Object()
    value.stamp.secs, value.stamp.nsecs = secs, nsecs
    value.frame_id = frame
    return value


class RecorderChecks(unittest.TestCase):
    def test_exact_header_rejects_other_time_sequence_or_frame(self):
        baseline = recorder.frame_key(recorder.header_dict(header()))
        for value in [header(seq=2), header(nsecs=4), header(frame='detection')]:
            self.assertNotEqual(baseline, recorder.frame_key(recorder.header_dict(value)))

    def test_cache_evicts_oldest_frame(self):
        cache = recorder.ImageCache(2)
        cache.put('first', 1)
        cache.put('second', 2)
        cache.put('third', 3)
        self.assertIsNone(cache.get('first'))
        self.assertEqual(cache.get('second'), 2)
        self.assertEqual(cache.latest(), 3)

    def test_nonfinite_score_is_serializable_unknown(self):
        self.assertIsNone(recorder.finite_number(float('nan')))
        self.assertIsNone(recorder.finite_number(float('inf')))
        self.assertEqual(recorder.finite_number(0.5), 0.5)

    def test_class_id_is_preserved_with_pixel_coordinates(self):
        box = Object()
        box.Class, box.id, box.probability = 'chair', 56, 0.49
        box.xmin, box.ymin, box.xmax, box.ymax = 10, 20, 50, 60
        message = Object()
        message.bounding_boxes = [box]
        result = recorder.boxes_list(message)[0]
        self.assertEqual(result['class_id'], 56)
        self.assertEqual(result['class'], 'chair')
        self.assertEqual(result['xmax'], 50)

    def test_defaults_are_bounded_and_personal(self):
        args = recorder.parse_args([])
        self.assertEqual(args.output, '~/fahad/detection_tests')
        self.assertEqual(args.duration, 60)
        self.assertEqual(args.rate, 2)

    def test_unmatched_record_keeps_boxes_without_inventing_image(self):
        args = recorder.parse_args([])
        capture = recorder.Recorder(args, None, None, None)
        capture.start = 10.0
        capture.events = io.StringIO()
        record = {'image_header': recorder.header_dict(header()),
                  'output_header': recorder.header_dict(header(nsecs=300000003)),
                  'boxes': [{'class': 'chair', 'score': 0.49}], '_received': 11.0}
        capture.process_record(record, None)
        saved = json.loads(capture.events.getvalue())
        self.assertEqual(saved['image_match'], 'unavailable')
        self.assertIsNone(saved['raw_image'])
        self.assertEqual(saved['boxes'][0]['class'], 'chair')
        self.assertAlmostEqual(saved['header_gap_s'], 0.3)

    def test_late_image_is_waited_for_before_declaring_unmatched(self):
        capture = recorder.Recorder(recorder.parse_args([]), None, None, None)
        capture.start = recorder.wall_time()
        capture.events = io.StringIO()
        record = {'image_header': recorder.header_dict(header()),
                  'output_header': recorder.header_dict(header()),
                  'boxes': [], '_received': recorder.wall_time()}
        waiting = capture.drain([record])
        self.assertEqual(len(waiting), 1)
        self.assertEqual(capture.events.getvalue(), '')
        capture.drain(waiting, final=True)
        self.assertEqual(json.loads(capture.events.getvalue())['image_match'], 'unavailable')


if __name__ == '__main__':
    unittest.main()
