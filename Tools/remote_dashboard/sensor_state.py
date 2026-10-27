"""Thread-safe latest sensor state and snapshots; no sensor or network startup."""
import collections
import threading
import uuid
from control import RehearsalControl, monotonic_clock
from settings import VERSION, TOPICS


class Dashboard(object):
    def __init__(self, ros=False, clock=None):
        self.clock = clock or monotonic_clock()
        self.started = self.clock()
        self.mode = 'ros_read_only' if ros else 'preview'
        self.boot_id = uuid.uuid4().hex
        self.key = uuid.uuid4().hex + uuid.uuid4().hex
        self.control = RehearsalControl(self.clock)
        self.drive = None
        self.lock = threading.RLock()
        self.frames = {}
        self.source_errors = {}
        self.observations, self.observation_received, self.observation_error = None, None, None
        self.scan = None
        self.scan_time = None
        self.last_scan_attempt = None
        self.scan_message_time = None
        self.scan_message_count = 0
        self.scan_arrivals = collections.deque(maxlen=80)
        self.scan_error = None
        self.scan_connections = None
        self.scan_connection_time = None
        self.ros_error = None
        self.map_grid, self.map_received, self.map_error = None, None, None
        self.map_revision, self.map_connections, self.map_connection_time = 0, None, None
        self.map_overlay, self.map_overlay_time = {}, None
        self.closed = threading.Event()

    def set_frame(self, source, data, received, frame_id, stamp, sequence):
        with self.lock:
            self.frames[source] = {'data': data, 'received': received,
                                   'frame_id': frame_id, 'stamp': stamp, 'sequence': sequence}
            self.source_errors.pop(source, None)

    def frame(self, source):
        with self.lock:
            result = self.frames.get(source)
            if result is None or self.clock() - result['received'] >= 2.0:
                return None
            return result['data']

    def status(self):
        with self.lock:
            now = self.clock()
            cameras = {}
            for source in ('rgb', 'yolo'):
                item = self.frames.get(source)
                age = max(0.0, now - item['received']) if item else None
                cameras[source] = {'topic': TOPICS[source], 'age_s': age,
                                   'available': age is not None and age < 2.0,
                                   'frame_id': item['frame_id'] if item else None,
                                   'stamp': item['stamp'] if item else None,
                                   'sequence': item['sequence'] if item else None,
                                   'error': self.source_errors.get(source)}
            age = max(0.0, now - self.scan_time) if self.scan_time is not None else None
            scan = dict(self.scan or {})
            message_age = max(0.0, now - self.scan_message_time) if self.scan_message_time is not None else None
            connection_age = max(0.0, now - self.scan_connection_time) if self.scan_connection_time is not None else None
            connections = self.scan_connections if connection_age is not None and connection_age < 2.0 else None
            available = age is not None and age < 2.0 and not self.scan_error and (connections is None or connections == 1)
            arrivals = [t for t in self.scan_arrivals if now - t < 2.0]
            rate = (len(arrivals) - 1) / (arrivals[-1] - arrivals[0]) if len(arrivals) >= 2 and arrivals[-1] > arrivals[0] else None
            if self.mode == 'preview':
                state = 'preview'
            elif self.scan_error and message_age is not None and message_age < 2.0:
                state = 'invalid'
            elif connections is not None and connections > 1:
                state = 'multiple_publishers'
            elif available:
                state = 'live' if scan.get('valid_samples') else 'no_valid_returns'
            elif connections == 0:
                state = 'no_publisher'
            elif message_age is not None or age is not None:
                state = 'stale'
            elif connections is not None and connections > 0:
                state = 'waiting_messages'
            else:
                state = 'waiting'
            scan.update({'topic': TOPICS['scan'], 'age_s': age,
                         'available': available, 'state': state,
                         'last_message_age_s': message_age, 'arrival_rate_hz': rate,
                         'messages_received': self.scan_message_count,
                         'publisher_connections': connections, 'error': self.scan_error})
            result = {'version': VERSION, 'mode': self.mode, 'boot_id': self.boot_id,
                    'uptime_s': max(0.0, now - self.started), 'cameras': cameras,
                    'scan': scan, 'ros_error': self.ros_error,
                    'motor_output': self.drive is not None}
            observation_age = now-self.observation_received+self.observations.get('source_age_s',0) if self.observation_received is not None and self.observations else None
            observation_available = self.mode != 'preview' and observation_age is not None and 0 <= observation_age < 2 and not self.observation_error
            result['observations'] = {'available': observation_available, 'age_s': observation_age,
                'records': self.observations['records'] if observation_available and self.observations else [],
                'image_header': self.observations['image_header'] if observation_available and self.observations else None,
                'error': self.observation_error, 'fusion': 'blocked_pending_calibration_tf_and_rectified_input',
                'persistence': 'none_latest_snapshot_only'}
        # Never take a control lock under the image lock: a drive health check
        # takes them in the opposite order. Snapshot only after releasing it.
        result['control'] = self.control.snapshot()
        return result

    def map_status(self, revision=None):
        with self.lock:
            now = self.clock()
            connections = self.map_connections if self.map_connection_time is not None and now-self.map_connection_time < 2 else None
            available = self.mode != 'preview' and self.map_grid is not None and not self.map_error and connections == 1
            result = {'available': available, 'topic': '/map', 'revision': self.map_revision,
                      'publisher_connections': connections, 'error': self.map_error,
                      'age_s': max(0, now-self.map_received) if self.map_received is not None else None,
                      'state': 'preview' if self.mode == 'preview' else 'invalid' if self.map_error else 'multiple_publishers' if connections and connections > 1 else 'map' if available else 'no_map',
                      'overlay': dict(self.map_overlay) if available and self.map_overlay_time is not None and now-self.map_overlay_time < .75 else {}}
            if available:
                result.update({k: v for k, v in self.map_grid.items() if k != 'cells'})
                if str(revision) != str(self.map_revision):
                    result['cells'] = self.map_grid['cells']
            return result
