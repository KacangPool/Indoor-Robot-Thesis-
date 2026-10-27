"""Explicit passive ROS1 sensor bag capture. Default mode only prints the plan.

Requires the existing robot ROS1 Python environment; no upgrades or drivers are
started. Raw captures contain private images: do not upload them to public GitHub.
"""
from __future__ import print_function
import argparse
import hashlib
import io
import json
import os
import threading
import time

from fahad_core.capture import TOPICS, CaptureBudget
from fahad_core.recording import write_json, free_megabytes
from record_detection_test import wall_time


def record(output, seconds=10, max_mib=512):
    # Imports only after explicit --record. No Publisher/launch/serial adapter.
    import rospy
    import rosbag
    from sensor_msgs.msg import Image, CameraInfo, LaserScan
    from darknet_ros_msgs.msg import BoundingBoxes
    from tf2_msgs.msg import TFMessage
    from nav_msgs.msg import Odometry
    types = {'sensor_msgs/Image': Image, 'sensor_msgs/CameraInfo': CameraInfo,
             'sensor_msgs/LaserScan': LaserScan, 'darknet_ros_msgs/BoundingBoxes': BoundingBoxes,
             'tf2_msgs/TFMessage': TFMessage, 'nav_msgs/Odometry': Odometry}
    budget = CaptureBudget(wall_time(), seconds, max_mib*1024*1024)
    target = os.path.abspath(output)
    parent = os.path.dirname(target)
    while not os.path.isdir(parent):
        parent = os.path.dirname(parent)
    available = free_megabytes(parent)
    if available is not None and available < max_mib+256:
        raise ValueError('Insufficient free space for bounded raw capture')
    os.makedirs(target)  # Raises if present; never overwrite an earlier capture.
    rospy.init_node('fahad_passive_fusion_capture', anonymous=True, disable_signals=False)
    lock = threading.Lock()
    subscribers = []
    bag = rosbag.Bag(os.path.join(target, 'sensors.bag'), 'w')
    active = [True]
    written = {topic: 0 for topic, _ in TOPICS}
    try:
        sim_time = bool(rospy.get_param('/use_sim_time', False))
    except Exception:
        sim_time = None
    def callback(message, topic):
        with lock:
            if not active[0]:
                return
            try:
                raw = io.BytesIO()
                message.serialize(raw)
                if budget.accept(topic, raw.tell(), wall_time()):
                    bag.write(topic, message, t=rospy.Time.now())
                    written[topic] += 1
            except Exception:
                budget.reason = 'capture_write_or_serialization_error'
                active[0] = False
    try:
        # Per-topic latched TF is preserved in the raw bag, not flattened/guessed.
        for topic, type_name in TOPICS:
            subscribers.append(rospy.Subscriber(topic, types[type_name], callback,
                                                callback_args=topic, queue_size=1,
                                                buff_size=8*1024*1024))
        while not rospy.is_shutdown():
            with lock:
                if not active[0] or budget.expired(wall_time()):
                    break
            time.sleep(.05)
    except KeyboardInterrupt:
        budget.reason = budget.reason or 'operator_interrupt'
    finally:
        with lock:
            active[0] = False
            budget.reason = budget.reason or 'ros_shutdown_or_capture_exit'
        for subscriber in subscribers:
            try:
                subscriber.unregister()
            except Exception:
                pass
        bag.close()
        summary = budget.summary()
        summary['accepted_before_write_counts'] = summary['counts']
        summary['counts'] = written
        summary['messages'] = sum(written.values())
        summary['missing_topics'] = [topic for topic, count in written.items() if not count]
        summary.update(schema_version=1, kind='raw_passive_sensor_capture',
                       file='sensors.bag', normalization='pending_operator_verified_calibration',
                       replay_policy='offline_analysis_only_never_rosbag_play',
                       privacy='Contains raw images and sensor data; keep local/private.',
                       duration_clock='monotonic' if hasattr(time, 'monotonic') else 'wall_time_regression_stops_capture',
                       ros_sim_time=sim_time)
        # Stream hash: do not load the potentially large bag into memory.
        hash_value = hashlib.sha256()
        with open(os.path.join(target, 'sensors.bag'), 'rb') as stream:
            for block in iter(lambda: stream.read(1024*1024), b''):
                hash_value.update(block)
        summary['sha256'] = hash_value.hexdigest()
        write_json(os.path.join(target, 'capture_manifest.json'), summary)
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', action='store_true')
    parser.add_argument('--output')
    parser.add_argument('--seconds', type=float, default=10)
    parser.add_argument('--max-mib', type=int, default=512)
    args = parser.parse_args(argv)
    try:
        CaptureBudget(0, args.seconds, args.max_mib*1024*1024)
        if not args.record:
            print(json.dumps({'mode': 'OFFLINE PLAN ONLY', 'topics': TOPICS,
                              'motor_output': False, 'requires': 'Explicit --record in existing ROS1 Python environment'}, indent=2))
            return 0
        if args.output is None:
            parser.error('--record requires a NEW --output directory')
        result = record(args.output, args.seconds, args.max_mib)
        print('Passive capture ended: %s; missing topics=%d. Calibration is NOT validated.' %
              (result['stop_reason'], len(result['missing_topics'])))
        return 0 if result['messages'] and result['stop_reason'] not in ('capture_write_or_serialization_error', 'capture_clock_regressed') else 1
    except Exception as error:
        print('Capture unavailable (%s): inspect output path, limits, free disk and existing ROS1 Python environment. No driver or movement was requested.' % type(error).__name__)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
