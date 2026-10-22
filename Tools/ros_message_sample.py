#!/usr/bin/env python
from __future__ import print_function

"""ROS 1 one-message reader; Python 2.7/3 compatible, no robot commands.
Run via ros_topic_report.sh for a process-level deadline.
Formatting functions can be tested without ROS installed.
"""
import math
import struct
import sys
import threading

from fahad_core.message_samples import (ARRAY_PREVIEW, LINE_LIMIT, finite,
                                      message_lines, image_samples, scan_summary, payload_lines)


def main():
    if len(sys.argv) != 3:
        print('Usage: ros_message_sample.py TOPIC PACKAGE/MessageType (use report wrapper for hard deadline)')
        return 2
    import rospy
    import roslib.message
    topic, type_name = sys.argv[1:]
    print('PHASE: load message class and initialize ROS reader')
    message_class = roslib.message.get_message_class(type_name)
    if message_class is None:
        print('[Message class unavailable: %s]' % type_name)
        return 2
    rospy.init_node('fahad_topic_sample', anonymous=True, disable_signals=True)
    ready = threading.Event()
    received = []

    def callback(message):
        if not ready.is_set():
            received.append(message)
            ready.set()

    print('PHASE: subscribe; wait up to 10 wall-clock seconds for one message')
    subscriber = rospy.Subscriber(topic, message_class, callback, queue_size=1, buff_size=2 ** 24)
    ready.wait(10.0)
    if not ready.is_set():
        print('[No message received during the 10-second subscription window; not proof of sensor failure.]')
        print('PHASE: unregister reader')
        subscriber.unregister()
        return 3
    print('MESSAGE RECEIVED: %s (%s)' % (topic, type_name))
    message = received[0]
    for line in message_lines(message):
        print(line)
    try:
        for line in payload_lines(message):
            print(line)
    except Exception as error:
        print('[Payload preview unavailable: %s]' % error)
    print('SAMPLE COMPLETE; unregistering reader')
    subscriber.unregister()
    return 0


if __name__ == '__main__':
    sys.exit(main())
