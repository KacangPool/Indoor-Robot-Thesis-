#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Timed ROS 1 RGB/detection capture; Python 2.7 and Python 3 compatible.

ROS imports are delayed so --help and the companion offline tests need no ROS.
Subscribe only: this script never starts drivers or publishes motion commands.
"""
from __future__ import print_function

import argparse
import collections
import datetime
import io
import json
import math
import os
import sys
import tempfile
import threading
import time


wall_time = getattr(time, 'monotonic', time.time)


from fahad_core.detections import finite_number, boxes_list
from fahad_core.recording import (header_dict, frame_key, ImageCache, write_json,
                                   append_json, free_megabytes)


class Recorder(object):
    def __init__(self, args, rospy, bridge, cv2):
        self.args, self.rospy, self.bridge, self.cv2 = args, rospy, bridge, cv2
        self.lock = threading.Lock()
        self.cache = ImageCache(args.cache_frames)
        self.queue = collections.deque()
        self.active = False
        self.start = None
        self.last_detection = None
        self.last_saved = None
        self.saved_keys = {}
        self.samples = []
        self.counts = collections.Counter()
        self.class_counts = collections.Counter()
        self.subscribers = []

    def on_image(self, message):
        with self.lock:
            self.cache.put(frame_key(header_dict(message.header)), message)
            if self.active:
                self.counts['rgb_messages_received'] += 1

    def on_boxes(self, message):
        received = wall_time()
        record = {'kind': 'detection', 'image_header': header_dict(message.image_header),
                  'output_header': header_dict(message.header),
                  'boxes': boxes_list(message), '_received': received}
        with self.lock:
            if not self.active:
                return
            self.counts['detection_messages_received'] += 1
            self.last_detection = received
            if len(self.queue) >= 256:
                self.counts['detection_queue_overflow'] += 1
                return
            self.queue.append(record)

    def save_image(self, message, boxes, mode):
        key = frame_key(header_dict(message.header))
        if key in self.saved_keys:
            return self.saved_keys[key]
        available = free_megabytes(self.session)
        if available is not None and available < 256:
            raise RuntimeError('Less than 256 MiB free; stopping capture.')
        bgr = self.bridge.imgmsg_to_cv2(message, desired_encoding='bgr8')
        index = len(self.samples) + 1
        raw_name = 'images/%04d_raw.jpg' % index
        preview_name = None
        if not self.cv2.imwrite(os.path.join(self.session, raw_name), bgr,
                                [int(self.cv2.IMWRITE_JPEG_QUALITY), 90]):
            raise RuntimeError('Could not save ' + raw_name)
        if boxes is not None:
            preview = bgr.copy()
            height, width = preview.shape[:2]
            for box in boxes:
                x1 = max(0, min(width - 1, box['xmin']))
                y1 = max(0, min(height - 1, box['ymin']))
                x2 = max(0, min(width - 1, box['xmax']))
                y2 = max(0, min(height - 1, box['ymax']))
                if x2 <= x1 or y2 <= y1:
                    continue
                self.cv2.rectangle(preview, (x1, y1), (x2, y2), (0, 255, 0), 2)
                label = box['class']
                if box['score'] is not None:
                    label += ' %.2f' % box['score']
                self.cv2.putText(preview, label, (x1, max(15, y1 - 5)),
                                 self.cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)
            preview_name = 'images/%04d_preview.jpg' % index
            if not self.cv2.imwrite(os.path.join(self.session, preview_name), preview,
                                    [int(self.cv2.IMWRITE_JPEG_QUALITY), 90]):
                raise RuntimeError('Could not save ' + preview_name)
        sample = {'kind': 'image_sample', 'sample': index, 'mode': mode,
                  'elapsed_s': wall_time() - self.start,
                  'image_header': header_dict(message.header),
                  'raw_image': raw_name, 'preview_image': preview_name,
                  'width': int(message.width), 'height': int(message.height),
                  'boxes': boxes}
        self.saved_keys[key] = sample
        self.samples.append(sample)
        self.last_saved = wall_time()
        self.counts['images_saved'] += 1
        append_json(self.events, sample)
        return sample

    def process_record(self, record, message):
        record['elapsed_s'] = record.pop('_received') - self.start
        record['raw_image'] = None
        record['preview_image'] = None
        record['image_match'] = 'exact_header' if message is not None else 'unavailable'
        key = frame_key(record['image_header'])
        sample = self.saved_keys.get(key)
        due = self.last_saved is None or wall_time() - self.last_saved >= 1.0 / self.args.rate
        if message is not None and sample is None and due:
            sample = self.save_image(message, record['boxes'], 'matched_detection')
        if sample is not None:
            record['raw_image'] = sample['raw_image']
            record['preview_image'] = sample['preview_image']
        output_stamp = record['output_header']
        image_stamp = record['image_header']
        record['header_gap_s'] = (output_stamp['secs'] - image_stamp['secs'] +
                                 (output_stamp['nsecs'] - image_stamp['nsecs']) / 1e9)
        self.counts['detection_records_written'] += 1
        if message is None:
            self.counts['detection_images_unavailable'] += 1
        for box in record['boxes']:
            self.class_counts[box['class']] += 1
        append_json(self.events, record)

    def drain(self, pending, final=False):
        now = wall_time()
        waiting = []
        for record in pending:
            with self.lock:
                message = self.cache.get(frame_key(record['image_header']))
            if message is None and not final and now - record['_received'] < 0.75:
                waiting.append(record)
                continue
            self.process_record(record, message)
        return waiting

    def run(self, Image, BoundingBoxes):
        root = os.path.abspath(os.path.expanduser(self.args.output))
        if not os.path.isdir(root):
            os.makedirs(root)
        available = free_megabytes(root)
        if available is not None and available < 256:
            raise RuntimeError('Less than 256 MiB free in output location.')
        self.session = tempfile.mkdtemp(
            prefix=datetime.datetime.now().strftime('test_%Y%m%d_%H%M%S_'), dir=root)
        os.mkdir(os.path.join(self.session, 'images'))
        write_json(os.path.join(self.session, 'session.json'), {
            'schema_version': 1, 'label': self.args.label, 'notes': self.args.notes,
            'local_start_time': datetime.datetime.now().isoformat(),
            'requested_duration_s': self.args.duration, 'requested_snapshot_rate_hz': self.args.rate,
            'image_topic': self.args.image_topic, 'boxes_topic': self.args.boxes_topic,
            'cache_frames': self.args.cache_frames, 'jpeg_quality': 90,
            'matching': 'identical image stamp, sequence and frame_id',
            'limitation': 'Missing box messages mean unknown detector status, not confirmed empty scene.'})
        self.events = io.open(os.path.join(self.session, 'events.jsonl'), 'w', encoding='utf-8')
        print('Output folder: ' + self.session)
        print('Starting in %.1f seconds. Duration: %.1f seconds.' %
              (self.args.delay, self.args.duration))
        pending = []
        status = 'completed'
        error = None
        try:
            self.subscribers = [
                self.rospy.Subscriber(self.args.image_topic, Image, self.on_image,
                                      queue_size=1, buff_size=4 * 1024 * 1024),
                self.rospy.Subscriber(self.args.boxes_topic, BoundingBoxes, self.on_boxes,
                                      queue_size=30)]
            delay_end = wall_time() + self.args.delay
            while wall_time() < delay_end and not self.rospy.is_shutdown():
                time.sleep(0.05)
            if self.rospy.is_shutdown():
                status = 'interrupted_before_capture'
                return 1
            self.start = wall_time()
            with self.lock:
                self.active = True
            print('RECORDING. Move into your test position now.')
            next_progress = self.start + 5
            while wall_time() - self.start < self.args.duration and not self.rospy.is_shutdown():
                with self.lock:
                    pending.extend(self.queue)
                    self.queue.clear()
                    latest = self.cache.latest()
                    last_detection = self.last_detection
                pending = self.drain(pending)
                now = wall_time()
                # Capture negative scenes even when this detector publishes no boxes.
                # A snapshot without a box message is explicitly UNKNOWN, never labelled empty.
                due = self.last_saved is None or now - self.last_saved >= 1.0 / self.args.rate
                quiet = last_detection is None or now - last_detection > 1.0
                if due and quiet and now - self.start > 1.0 and latest is not None:
                    self.save_image(latest, None, 'no_recent_detection_message')
                if now >= next_progress:
                    print('%.0fs / %.0fs; %d snapshots, %d detection records' %
                          (now - self.start, self.args.duration, len(self.samples),
                           self.counts['detection_records_written']))
                    next_progress = now + 5
                time.sleep(0.02)
            if self.rospy.is_shutdown():
                status = 'interrupted'
            with self.lock:
                self.active = False
                pending.extend(self.queue)
                self.queue.clear()
            self.drain(pending, final=True)
            if not self.counts['rgb_messages_received']:
                status = 'no_rgb_messages'
            elif not self.counts['detection_messages_received']:
                status = 'no_detection_messages_verify_detector'
        except KeyboardInterrupt:
            status = 'interrupted'
        except Exception as exc:
            status = 'error'
            error = str(exc)
            raise
        finally:
            with self.lock:
                self.active = False
            for subscriber in self.subscribers:
                subscriber.unregister()
            self.events.close()
            self.counts['detection_records_not_written'] = max(
                0, self.counts['detection_messages_received'] -
                self.counts['detection_records_written'] -
                self.counts['detection_queue_overflow'])
            summary = {'status': status, 'error': error,
                       'elapsed_s': wall_time() - self.start if self.start is not None else 0,
                       'counts': dict(self.counts), 'class_hypothesis_counts': dict(self.class_counts),
                       'warning': 'Counts include repeated/overlapping hypotheses; these are not unique objects or accuracy.'}
            write_json(os.path.join(self.session, 'summary.json'), summary)
            with io.open(os.path.join(self.session, 'report.txt'), 'w', encoding='utf-8') as stream:
                stream.write(u'Detection test: %s\nStatus: %s\n' % (self.args.label, status))
                stream.write(u'Notes: %s\n\n' % self.args.notes)
                stream.write(json.dumps(summary, indent=2, ensure_ascii=True) + u'\n\n')
                for sample in self.samples:
                    labels = 'detector status unknown'
                    if sample['boxes'] is not None:
                        labels = ', '.join('%s (%s)' % (box['class'], box['score'])
                                           for box in sample['boxes']) or 'explicit empty box array'
                    stream.write(u'%04d | %.2fs | %s | %s\n' %
                                 (sample['sample'], sample['elapsed_s'], sample['raw_image'], labels))
            print('Finished: ' + status)
            print('Copy this whole folder: ' + self.session)
        return 0 if status == 'completed' else 1


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description='Save timed RGB snapshots and ROS detection records.')
    parser.add_argument('--duration', type=float, default=60, help='Capture seconds, 1-600 (default 60).')
    parser.add_argument('--delay', type=float, default=10, help='Preparation seconds, 0-120 (default 10).')
    parser.add_argument('--rate', type=float, default=2, help='Maximum snapshot rate, 0.2-5 Hz (default 2).')
    parser.add_argument('--label', default='pilot', help='Description such as empty_room or person_2m.')
    parser.add_argument('--notes', default='', help='Measured distance, posture, lighting and camera tilt.')
    parser.add_argument('--output', default='~/fahad/detection_tests', help='Parent folder for new sessions.')
    parser.add_argument('--image-topic', default='/camera/rgb/image_raw')
    parser.add_argument('--boxes-topic', default='/darknet_ros/bounding_boxes')
    parser.add_argument('--cache-frames', type=int, default=60, help='Raw-image cache, 10-120 frames.')
    args = parser.parse_args(argv)
    for name, minimum, maximum in [('duration', 1, 600), ('delay', 0, 120), ('rate', 0.2, 5)]:
        value = getattr(args, name)
        if math.isnan(value) or math.isinf(value) or not minimum <= value <= maximum:
            parser.error('--%s must be between %s and %s' % (name, minimum, maximum))
    if not 10 <= args.cache_frames <= 120:
        parser.error('--cache-frames must be between 10 and 120')
    return args


def main():
    args = parse_args()
    try:
        import rospy
        import cv2
        from cv_bridge import CvBridge
        from sensor_msgs.msg import Image
        from darknet_ros_msgs.msg import BoundingBoxes
    except ImportError as exc:
        print('Required robot ROS/Python module missing: %s' % exc, file=sys.stderr)
        print('Source ~/wheeltec_robot/devel/setup.bash and use the robot ROS Python environment.',
              file=sys.stderr)
        return 2
    rospy.init_node('fahad_detection_test_recorder', anonymous=True)
    return Recorder(args, rospy, CvBridge(), cv2).run(Image, BoundingBoxes)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        print('Recorder stopped: %s' % exc, file=sys.stderr)
        sys.exit(1)
