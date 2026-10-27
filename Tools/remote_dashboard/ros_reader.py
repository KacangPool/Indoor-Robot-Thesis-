"""ROS input adapter: subscriptions, image encoding and optional TF overlays.

Importing this module is motor-free and does not import ROS/OpenCV. Dependencies
are acquired only when RosReader is explicitly constructed.
"""
import math
import threading
from settings import TOPICS
from sensor_models import occupancy_summary, planar_pose, scan_summary


class RosReader(object):
    def __init__(self, dashboard, fps):
        # Keep imports here: laptop preview/tests need no ROS/OpenCV installation.
        import rospy
        import cv2
        from cv_bridge import CvBridge
        from sensor_msgs.msg import Image, LaserScan
        from nav_msgs.msg import OccupancyGrid
        self.rospy, self.cv2, self.bridge = rospy, cv2, CvBridge()
        self.dashboard, self.fps = dashboard, fps
        self.pending = {}
        self.lock = threading.Lock()
        rospy.init_node('fahad_dashboard_reader', anonymous=True, disable_signals=True)
        self.subscribers = []
        try:
            from darknet_ros_msgs.msg import BoundingBoxes
            self.subscribers.append(rospy.Subscriber(TOPICS['boxes'], BoundingBoxes,
                                                     self.boxes_callback, queue_size=1))
        except ImportError:
            dashboard.observation_error = 'darknet_ros_msgs unavailable; camera-only labels disabled'
        for source in ('rgb', 'yolo'):
            self.subscribers.append(rospy.Subscriber(
                TOPICS[source], Image, self.image_callback, callback_args=source,
                queue_size=1, buff_size=2097152))
        self.scan_subscriber = rospy.Subscriber(TOPICS['scan'], LaserScan,
                                               self.scan_callback, queue_size=1)
        self.subscribers.append(self.scan_subscriber)
        self.pending_map = None
        self.map_subscriber = rospy.Subscriber('/map', OccupancyGrid, self.map_callback, queue_size=1, buff_size=2097152)
        self.subscribers.append(self.map_subscriber)
        self.tf_buffer = self.tf_listener = None
        try:
            import tf2_ros
            self.tf_buffer = tf2_ros.Buffer()
            self.tf_listener = tf2_ros.TransformListener(self.tf_buffer)
        except ImportError:
            pass  # Map still works; never invent a pose or align odometry blindly.
        self.map_worker = threading.Thread(target=self.map_loop)
        self.map_worker.daemon = True
        self.map_worker.start()
        self.worker = threading.Thread(target=self.encode_loop)
        self.worker.daemon = True
        self.worker.start()

    def image_callback(self, message, source):
        with self.lock:
            self.pending[source] = (message, self.dashboard.clock())

    def boxes_callback(self, message):
        try:
            from fahad_core.observations import camera_observations, source_age
            observations = camera_observations(message)
            observations['source_age_s'] = max(0, source_age(observations, self.rospy.Time.now().to_sec()))
            with self.dashboard.lock:
                self.dashboard.observations = observations
                self.dashboard.observation_received = self.dashboard.clock()
                self.dashboard.observation_error = None
        except (ImportError, AttributeError, TypeError, ValueError, OverflowError, UnicodeError):
            with self.dashboard.lock:
                self.dashboard.observations = None
                self.dashboard.observation_error = 'Invalid/stale source boxes or missing shared dependency'

    def map_callback(self, message):
        with self.lock:
            self.pending_map = (message, self.dashboard.clock())

    def map_loop(self):
        while not self.dashboard.closed.is_set() and not self.rospy.is_shutdown():
            with self.lock:
                pending, self.pending_map = self.pending_map, None
            if pending:
                message, received = pending
                try:
                    grid = occupancy_summary(message)
                    with self.dashboard.lock:
                        if grid != self.dashboard.map_grid:
                            self.dashboard.map_revision += 1
                        self.dashboard.map_grid, self.dashboard.map_received, self.dashboard.map_error = grid, received, None
                except (AttributeError, TypeError, ValueError, OverflowError):
                    with self.dashboard.lock:
                        self.dashboard.map_grid = None
                        self.dashboard.map_error = 'Invalid/oversized /map; maximum 1,000,000 source cells, planar origin required'
            try:
                count = self.map_subscriber.get_num_connections()
            except Exception:
                count = None
            with self.dashboard.lock:
                self.dashboard.map_connections, self.dashboard.map_connection_time = count, self.dashboard.clock()
                grid, scan, scan_time = self.dashboard.map_grid, self.dashboard.scan, self.dashboard.scan_time
            overlay = {}
            if grid and self.tf_buffer:
                try:
                    # The isolated base launch explicitly uses base_footprint.
                    transform = self.tf_buffer.lookup_transform(grid['frame'], 'base_footprint', self.rospy.Time(0), self.rospy.Duration(0))
                    age = self.rospy.Time.now().to_sec()-transform.header.stamp.to_sec()
                    if transform.header.stamp.to_sec() > 0 and 0 <= age < .5:
                        overlay['robot'] = planar_pose(transform.transform.translation, transform.transform.rotation)
                except Exception:
                    pass
                if scan and not self.dashboard.scan_error and self.dashboard.scan_connections == 1 and scan_time is not None and self.dashboard.clock()-scan_time < .75 and scan.get('stamp') and scan.get('frame') and 0 <= self.rospy.Time.now().to_sec()-scan['stamp'] < .5:
                    try:
                        transform = self.tf_buffer.lookup_transform(grid['frame'], scan['frame'], self.rospy.Time.from_sec(scan['stamp']), self.rospy.Duration(0))
                        pose = planar_pose(transform.transform.translation, transform.transform.rotation)
                        c, s = math.cos(pose['yaw']), math.sin(pose['yaw'])
                        overlay['scan'] = [[pose['x']+c*x-s*y, pose['y']+s*x+c*y] for x,y in scan['points']]
                        # Preserve distance from the laser, NOT map origin.
                        overlay['scan_ranges_m'] = [math.hypot(x,y) for x,y in scan['points']]
                    except Exception:
                        pass
            with self.dashboard.lock:
                self.dashboard.map_overlay, self.dashboard.map_overlay_time = overlay, self.dashboard.clock()
            self.dashboard.closed.wait(.5)

    def scan_callback(self, message):
        now = self.dashboard.clock()
        with self.dashboard.lock:
            self.dashboard.scan_message_time = now
            self.dashboard.scan_message_count += 1
            self.dashboard.scan_arrivals.append(now)
            if self.dashboard.last_scan_attempt is not None and now - self.dashboard.last_scan_attempt < 0.2:
                return
            self.dashboard.last_scan_attempt = now
        try:
            summary = scan_summary(message)
            # Optional acquisition-timed body pose in the actual laser frame.
            # Missing TF means no car pose; never assume sensor +X is car front.
            buffer = getattr(self, 'tf_buffer', None)
            if buffer and summary.get('stamp') and 0 <= self.rospy.Time.now().to_sec()-summary['stamp'] < .5:
                try:
                    transform = buffer.lookup_transform(summary['frame'], 'base_footprint',
                        self.rospy.Time.from_sec(summary['stamp']), self.rospy.Duration(0))
                    summary['robot_pose'] = planar_pose(transform.transform.translation, transform.transform.rotation)
                except Exception:
                    pass
            with self.dashboard.lock:
                self.dashboard.scan = summary
                self.dashboard.scan_time = now
                self.dashboard.scan_error = None
        except (TypeError, ValueError, OverflowError):
            # Invalidate immediately: don't keep showing old points as current.
            with self.dashboard.lock:
                self.dashboard.scan, self.dashboard.scan_time = None, None
                self.dashboard.scan_error = 'Invalid LaserScan geometry or ranges; inspect /scan'

    def encode_loop(self):
        while not self.dashboard.closed.is_set() and not self.rospy.is_shutdown():
            # Local subscriber connection count only; no ROS-master RPC, shell
            # command, driver launch or graph query in HTTP/control handlers.
            try:
                connections = self.scan_subscriber.get_num_connections()
            except Exception:
                connections = None
            with self.dashboard.lock:
                self.dashboard.scan_connections = connections
                self.dashboard.scan_connection_time = self.dashboard.clock()
            with self.lock:
                batch, self.pending = self.pending, {}
            for source, (message, received) in batch.items():
                try:
                    if self.dashboard.clock() - received >= 2.0:
                        continue
                    # Bound work; camera is currently reported as 640x480.
                    if not 0 < message.width <= 1920 or not 0 < message.height <= 1080:
                        raise ValueError('Image dimensions outside preview limits')
                    image = self.bridge.imgmsg_to_cv2(message, desired_encoding='bgr8')
                    height, width = image.shape[:2]
                    if width > 640:
                        image = self.cv2.resize(image, (640, max(1, int(height * 640.0 / width))))
                    okay, encoded = self.cv2.imencode('.jpg', image, [self.cv2.IMWRITE_JPEG_QUALITY, 70])
                    if not okay:
                        raise ValueError('JPEG encoding failed')
                    data = encoded.tobytes() if hasattr(encoded, 'tobytes') else encoded.tostring()
                    self.dashboard.set_frame(source, data, received, message.header.frame_id,
                                             message.header.stamp.to_sec(), message.header.seq)
                except Exception:
                    with self.dashboard.lock:
                        self.dashboard.frames.pop(source, None)
                        self.dashboard.source_errors[source] = 'Image conversion failed; inspect ROS format/dependencies'
            self.dashboard.closed.wait(1.0 / self.fps)
        if not self.dashboard.closed.is_set():
            self.dashboard.ros_error = 'ROS reader stopped; check the ROS master and nodes'

    def close(self):
        for subscriber in self.subscribers:
            subscriber.unregister()
        self.rospy.signal_shutdown('Dashboard closed')
        self.worker.join(2.0)
        if hasattr(self, 'map_worker'):
            self.map_worker.join(2.0)
