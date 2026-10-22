#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Person-only ROS 1 output; no model changes and no movement commands.

Python 2.7/3 syntax. ROS imports are delayed for offline tests and --help.
The input image header, pixel coordinates, class IDs and scores are preserved.
"""
from __future__ import print_function

import argparse
import math
import sys


from fahad_core.detections import select_person_boxes, filtered_message


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description='Publish person-only boxes without changing YOLO or moving the robot.')
    parser.add_argument('--threshold', type=float, default=0.5, help='Trial score cutoff, default 0.5; not a validated optimum.')
    parser.add_argument('--input-topic', default='/darknet_ros/bounding_boxes')
    parser.add_argument('--output-topic', default='/fahad/person_boxes')
    args = parser.parse_args(argv)
    if math.isnan(args.threshold) or math.isinf(args.threshold) or not 0 <= args.threshold <= 1:
        parser.error('--threshold must be finite and between 0 and 1')
    if not args.input_topic.startswith('/'):
        parser.error('--input-topic must be an absolute ROS topic name')
    if not args.output_topic.startswith('/fahad/'):
        parser.error('--output-topic must stay under /fahad/ to preserve original robot topics')
    if args.output_topic == args.input_topic:
        parser.error('input and output topics must differ')
    return args


def main(argv=None):
    args = parse_args(argv)
    try:
        import rospy
        from darknet_ros_msgs.msg import BoundingBoxes
    except ImportError as error:
        print('ROS imports unavailable: %s' % error, file=sys.stderr)
        print('Run on the robot after sourcing ~/wheeltec_robot/devel/setup.bash; do not replace ROS/Python.', file=sys.stderr)
        return 2

    rospy.init_node('fahad_person_detection_filter', anonymous=True)
    input_topic = rospy.resolve_name(args.input_topic)
    output_topic = rospy.resolve_name(args.output_topic)
    if input_topic == output_topic or not output_topic.startswith('/fahad/'):
        rospy.logerr('Resolved topics must differ and output must remain under /fahad/.')
        return 2
    publisher = rospy.Publisher(output_topic, BoundingBoxes, queue_size=5, latch=False)

    def callback(message):
        result = filtered_message(message, BoundingBoxes, args.threshold)
        publisher.publish(result)
        rospy.loginfo_throttle(3.0, 'Person filter: retained %d / %d received boxes at %.2f' %
                               (len(result.bounding_boxes), len(message.bounding_boxes), args.threshold))

    subscriber = rospy.Subscriber(input_topic, BoundingBoxes, callback, queue_size=5)
    rospy.loginfo('Read %s -> publish %s; person score >= %.2f. No motion output.' %
                  (input_topic, output_topic, args.threshold))
    rospy.loginfo('Original YOLO display/data unchanged. Silence is unknown, not proof that no person is present.')
    rospy.spin()
    subscriber.unregister()
    return 0


if __name__ == '__main__':
    sys.exit(main())
