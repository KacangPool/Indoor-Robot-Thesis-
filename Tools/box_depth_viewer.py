#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Read-only RGB/depth patch viewer for ROS 1, Python 2.7/3.

No detections, motion, parameter writes, automatic files or calibration changes.
Same-pixel sampling is a registration hypothesis, NOT validated object distance.
"""
from __future__ import print_function

import argparse
import math
import sys
import threading
import time

import numpy as np


# Compatibility exports; implementations are reusable without the GUI.
from fahad_core.depth import depth_metres, patch_stats, pair_problem


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rgb-topic', default='/camera/rgb/image_raw')
    parser.add_argument('--depth-topic', default='/camera/depth_registered/image_raw')
    parser.add_argument('--radius', type=int, default=5, help='Patch radius in pixels (default: 11x11 patch)')
    args = parser.parse_args(argv)
    if not 0 <= args.radius <= 30:
        parser.error('--radius must be between 0 and 30')
    if not args.rgb_topic.startswith('/') or not args.depth_topic.startswith('/'):
        parser.error('Use absolute topic names')
    if args.rgb_topic == args.depth_topic:
        parser.error('Colour and depth topics must differ')
    return args


def main(argv=None):
    args = parse_args(argv)
    try:
        import cv2
        import rospy
        import message_filters
        from cv_bridge import CvBridge
        from sensor_msgs.msg import Image
    except ImportError as error:
        print('Missing existing ROS/GUI dependency: %s' % error, file=sys.stderr)
        print('Run on the robot desktop after sourcing its ROS workspace. Do not upgrade ROS/Python.', file=sys.stderr)
        return 2

    rospy.init_node('fahad_box_depth_viewer', anonymous=True)
    bridge = CvBridge()
    lock = threading.Lock()
    state = dict(latest=None, displayed=None, selected=None, frozen=False, overlay=False)
    max_delta = 0.05
    stale_seconds = 1.0

    def receive(rgb, depth):
        with lock:
            state['latest'] = (rgb, depth, time.time())

    rgb_sub = message_filters.Subscriber(args.rgb_topic, Image, queue_size=1, buff_size=2**22)
    depth_sub = message_filters.Subscriber(args.depth_topic, Image, queue_size=1, buff_size=2**22)
    sync = message_filters.ApproximateTimeSynchronizer([rgb_sub, depth_sub], 5, max_delta)
    sync.registerCallback(receive)
    title = 'Box depth: RGB left | depth right | space freeze | o overlay | c clear | q quit'
    try:
        cv2.namedWindow(title, cv2.WINDOW_AUTOSIZE)
    except Exception as error:
        print('Cannot open desktop window: %s' % error, file=sys.stderr)
        print('Use a terminal on the robot graphical desktop, not a headless SSH session.', file=sys.stderr)
        return 2

    def describe(displayed, selected):
        colour, metres, received, rgb_stamp, depth_stamp, frame, encoding = displayed
        result = patch_stats(metres, selected[0], selected[1], args.radius)
        if result['median'] is None:
            reading = 'NO FINITE POSITIVE DEPTH'
        else:
            reading = 'median %.3f m | min/max %.3f/%.3f m' % (
                result['median'], result['minimum'], result['maximum'])
        detail = 'patch (%d,%d) | numeric %.1f%% | in 0.4-2m %.1f%% | %s' % (
            result['x'], result['y'], result['valid_percent'], result['in_range_percent'], reading)
        return result, detail

    def click(event, x, y, flags, param):
        displayed = state['displayed']
        if event != cv2.EVENT_LBUTTONDOWN or displayed is None:
            return
        if not state['frozen'] and time.time()-displayed[2] > stale_seconds:
            print('Click ignored: displayed pair is stale. Wait for live data.')
            return
        height, width = displayed[1].shape
        if not (0 <= y < height and 0 <= x < width*2):
            return
        state['selected'] = (x % width, y)
        result, detail = describe(displayed, state['selected'])
        print('SELECTED | %s | frame %s | encoding %s | rgb %.9f depth %.9f | frozen %s' % (
            detail, displayed[5], displayed[6], displayed[3], displayed[4], state['frozen']))

    cv2.setMouseCallback(title, click)
    print('Read-only: %s + %s' % (args.rgb_topic, args.depth_topic))
    print('Click the centre of the visible box face, away from its edges. Space freezes/unfreezes.')
    print('Depth colours: dark=near, light=far on fixed 0.4-2m scale; magenta=positive outside that range; black=invalid.')
    print('Same-pixel correspondence is NOT calibrated; approximately 1m is not ground truth. No motion output.')
    last_identity = None
    last_report = 0.0
    try:
        while not rospy.is_shutdown():
            with lock:
                candidate = state['latest']
            if not state['frozen'] and candidate is not None:
                rgb_msg, depth_msg, received = candidate
                identity = (rgb_msg.header.stamp.to_nsec(), depth_msg.header.stamp.to_nsec())
                rgb_stamp, depth_stamp = rgb_msg.header.stamp.to_sec(), depth_msg.header.stamp.to_sec()
                if time.time()-received > stale_seconds or rospy.Time.now().to_sec()-min(rgb_stamp, depth_stamp) > stale_seconds:
                    state['displayed'] = None
                    rospy.logwarn_throttle(3.0, 'Stale pair: numeric readings disabled.')
                elif identity != last_identity:
                    last_identity = identity
                    try:
                        colour = bridge.imgmsg_to_cv2(rgb_msg, desired_encoding='bgr8')
                        metres = depth_metres(bridge.imgmsg_to_cv2(depth_msg, desired_encoding='passthrough'), depth_msg.encoding)
                        problem = pair_problem(colour.shape, metres.shape, rgb_stamp, depth_stamp,
                                               rgb_msg.header.frame_id, depth_msg.header.frame_id, max_delta,
                                               rospy.Time.now().to_sec())
                        if problem:
                            raise ValueError(problem)
                        state['displayed'] = (colour, metres, received, rgb_stamp, depth_stamp,
                                              rgb_msg.header.frame_id, depth_msg.encoding)
                    except Exception as error:
                        state['displayed'] = None
                        rospy.logwarn_throttle(3.0, 'Pair rejected: %s' % error)

            displayed = state['displayed']
            if displayed is None:
                canvas = np.zeros((240, 900, 3), dtype=np.uint8)
                cv2.putText(canvas, 'WAITING: fresh RGB/depth pair with matching size/frame', (10, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
                rospy.logwarn_throttle(5.0, 'Waiting for usable RGB/depth pair (header tolerance 50 ms). Check topics/frames; no settings changed.')
            else:
                colour, metres = displayed[:2]
                finite = np.isfinite(metres)
                positive = np.zeros(metres.shape, dtype=np.bool_)
                positive[finite] = metres[finite] > 0
                inside = np.zeros(metres.shape, dtype=np.bool_)
                inside[positive] = (metres[positive] >= 0.4) & (metres[positive] <= 2.0)
                grey = np.zeros(metres.shape, dtype=np.uint8)
                grey[inside] = (40+215*(metres[inside]-0.4)/1.6).astype(np.uint8)
                depth_view = np.repeat(grey[:, :, None], 3, axis=2)
                depth_view[positive & ~inside] = (255, 0, 255)
                left = colour.copy()
                if state['overlay']:
                    blend = cv2.addWeighted(colour, 0.7, depth_view, 0.3, 0)
                    left[positive] = blend[positive]
                footer = np.zeros((80, colour.shape[1]*2, 3), dtype=np.uint8)
                detail = 'Click inside box face. o=depth overlay. Space=freeze. q=quit.'
                if state['selected'] is not None:
                    x, y = state['selected']
                    if x < metres.shape[1] and y < metres.shape[0]:
                        result, detail = describe(displayed, state['selected'])
                        x0, y0, x1, y1 = result['bounds']
                        for view in (left, depth_view):
                            cv2.rectangle(view, (x0, y0), (x1-1, y1-1), (0, 255, 0), 1)
                        if time.time()-last_report >= 2.0:
                            print('%s | %s | dt %.1f ms | rgb %.9f depth %.9f' % (
                                'FROZEN (historical)' if state['frozen'] else 'LIVE', detail,
                                abs(displayed[3]-displayed[4])*1000, displayed[3], displayed[4]))
                            last_report = time.time()
                    else:
                        state['selected'] = None
                cv2.putText(footer, detail, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(footer, '%s | dt %.1f ms | range colours are NOT accuracy | alignment unverified' % (
                    'FROZEN - historical' if state['frozen'] else 'LIVE', abs(displayed[3]-displayed[4])*1000),
                    (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 1)
                canvas = np.vstack((np.hstack((left, depth_view)), footer))
            cv2.imshow(title, canvas)
            key = cv2.waitKey(200) & 0xff  # At most about 5 GUI/decode iterations per second.
            if key in (ord('q'), 27):
                break
            if key == ord(' ') and displayed is not None:
                state['frozen'] = not state['frozen']
                print('FROZEN: historical pair' if state['frozen'] else 'LIVE: resumed')
            elif key == ord('o'):
                state['overlay'] = not state['overlay']
            elif key == ord('c'):
                state['selected'] = None
    except KeyboardInterrupt:
        pass
    finally:
        rgb_sub.unregister()
        depth_sub.unregister()
        cv2.destroyAllWindows()
    return 0


if __name__ == '__main__':
    sys.exit(main())
