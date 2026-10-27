"""Fixed passive sensor-capture policy. No ROS, IO or service startup."""
from .fusion_geometry import number

TOPICS = (
    ('/camera/rgb/image_raw', 'sensor_msgs/Image'),
    ('/camera/rgb/image_rect_color', 'sensor_msgs/Image'),
    ('/camera/rgb/camera_info', 'sensor_msgs/CameraInfo'),
    ('/camera/depth_registered/image_raw', 'sensor_msgs/Image'),
    ('/camera/depth_registered/camera_info', 'sensor_msgs/CameraInfo'),
    ('/darknet_ros/bounding_boxes', 'darknet_ros_msgs/BoundingBoxes'),
    ('/scan', 'sensor_msgs/LaserScan'), ('/tf', 'tf2_msgs/TFMessage'),
    ('/tf_static', 'tf2_msgs/TFMessage'), ('/odom', 'nav_msgs/Odometry'))


class CaptureBudget(object):
    def __init__(self, start, seconds=10, max_bytes=512*1024*1024, max_messages=10000):
        self.start = number(start)
        self.seconds = number(seconds)
        if not 0 < self.seconds <= 120 or type(max_bytes) is not int or not 1024 <= max_bytes <= 1024**3 or type(max_messages) is not int or not 1 <= max_messages <= 100000:
            raise ValueError('Invalid finite capture limits')
        self.max_bytes, self.max_messages = max_bytes, max_messages
        self.counts = {topic: 0 for topic, _ in TOPICS}
        self.bytes = self.messages = 0
        self.reason = None

    def expired(self, now):
        elapsed = number(now)-self.start
        if elapsed < 0:
            self.reason = 'capture_clock_regressed'
        elif elapsed >= self.seconds:
            self.reason = self.reason or 'duration_limit'
        return self.reason is not None

    def accept(self, topic, size, now):
        if topic not in self.counts or type(size) is not int or not 0 < size <= 8*1024*1024:
            raise ValueError('Non-allowlisted topic or oversized message')
        if self.expired(now):
            return False
        if self.messages >= self.max_messages or self.bytes+size > self.max_bytes:
            self.reason = 'message_or_byte_limit'
            return False
        self.bytes += size
        self.messages += 1
        self.counts[topic] += 1
        return True

    def summary(self):
        return {'counts': dict(self.counts), 'serialized_message_bytes': self.bytes,
                'messages': self.messages, 'stop_reason': self.reason,
                'missing_topics': [key for key, count in self.counts.items() if not count],
                'limits': {'seconds': self.seconds, 'max_bytes': self.max_bytes,
                           'max_messages': self.max_messages},
                'calibration_validated': False, 'motor_output': False}
