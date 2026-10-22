#!/usr/bin/env python
from __future__ import print_function

"""Read-only ROS 1 camera monitor for RGB, registered depth, and calibration."""

import threading
import time

from fahad_core.camera_metrics import rgb_statistics, depth_statistics, camera_info_summary
import rospy
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import CameraInfo, Image


class CameraDiagnostics(object):
    def __init__(self):
        self.bridge = CvBridge()
        self.lock = threading.Lock()
        self.started = time.time()
        self.last_report = self.started
        self.rgb_count = 0
        self.depth_count = 0
        self.last_rgb_analysis = 0.0
        self.last_depth_analysis = 0.0
        self.rgb = None
        self.depth = None
        self.info = None

        self.rgb_topic = rospy.get_param("~rgb_topic", "/camera/rgb/image_raw")
        self.depth_topic = rospy.get_param(
            "~depth_topic", "/camera/depth_registered/image_raw"
        )
        self.info_topic = rospy.get_param(
            "~camera_info_topic", "/camera/rgb/camera_info"
        )
        self.report_interval = float(rospy.get_param("~report_interval", 2.0))
        self.analysis_interval = float(rospy.get_param("~analysis_interval", 0.5))

        rospy.Subscriber(self.rgb_topic, Image, self.rgb_callback, queue_size=1)
        rospy.Subscriber(self.depth_topic, Image, self.depth_callback, queue_size=1)
        rospy.Subscriber(self.info_topic, CameraInfo, self.info_callback, queue_size=1)

        print("Read-only camera monitor")
        print("  RGB:   {0}".format(self.rgb_topic))
        print("  Depth: {0}".format(self.depth_topic))
        print("  Info:  {0}".format(self.info_topic))
        print("Press Ctrl+C to stop. Percent-dark/bright are exposure indicators, not quality scores.\n")

    def rgb_callback(self, msg):
        now = time.time()
        with self.lock:
            self.rgb_count += 1
            if now - self.last_rgb_analysis < self.analysis_interval:
                return
            self.last_rgb_analysis = now
        try:
            image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
            result = {'width': msg.width, 'height': msg.height, 'encoding': msg.encoding}
            result.update(rgb_statistics(image))
            with self.lock:
                self.rgb = result
        except (CvBridgeError, ValueError, IndexError) as error:
            rospy.logwarn_throttle(5.0, "Could not analyse RGB image: %s", error)

    def depth_callback(self, msg):
        now = time.time()
        with self.lock:
            self.depth_count += 1
            if now - self.last_depth_analysis < self.analysis_interval:
                return
            self.last_depth_analysis = now
        try:
            image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")
            result = {'width': msg.width, 'height': msg.height, 'encoding': msg.encoding}
            result.update(depth_statistics(image, msg.encoding))
            with self.lock:
                self.depth = result
        except (CvBridgeError, ValueError) as error:
            rospy.logwarn_throttle(5.0, "Could not analyse depth image: %s", error)

    def info_callback(self, msg):
        result = camera_info_summary(msg)
        if result is None:
            return
        with self.lock:
            self.info = result

    def report(self):
        now = time.time()
        elapsed = now - self.last_report
        if elapsed < self.report_interval:
            return

        with self.lock:
            rgb = self.rgb
            depth = self.depth
            info = self.info
            rgb_fps = self.rgb_count / elapsed
            depth_fps = self.depth_count / elapsed
            self.rgb_count = 0
            self.depth_count = 0
            self.last_report = now

        print("--- {0:.1f} s ---".format(now - self.started))
        if rgb is None:
            print("RGB:   waiting for messages")
        else:
            print(
                "RGB:   {width}x{height} {encoding} | {fps:.1f} fps | "
                "brightness {mean:.1f}/255 | dark {dark:.1f}% | bright {bright:.1f}%".format(
                    fps=rgb_fps, **rgb
                )
            )

        if depth is None:
            print("Depth: waiting for messages")
        else:
            print(
                "Depth: {width}x{height} {encoding} | {fps:.1f} fps | valid {valid:.1f}% | "
                "min/median/max {min:.2f}/{median:.2f}/{max:.2f} m".format(
                    fps=depth_fps, **depth
                )
            )

        if info is None:
            print("Info:  waiting for CameraInfo")
        else:
            print(
                "Info:  frame {frame} | calibration {width}x{height} | "
                "fx/fy {fx:.1f}/{fy:.1f} px | cx/cy {cx:.1f}/{cy:.1f} | {distortion}".format(
                    **info
                )
            )
        print("")


def main():
    rospy.init_node("camera_diagnostics", anonymous=True)
    monitor = CameraDiagnostics()
    rate = rospy.Rate(10)
    while not rospy.is_shutdown():
        monitor.report()
        rate.sleep()


if __name__ == "__main__":
    main()
