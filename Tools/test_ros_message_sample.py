"""Offline formatting tests with synthetic data; not ROS integration tests."""
import struct
import unittest
import ros_message_sample as sample


class Message(object):
    def __init__(self, kind, fields):
        self._type = kind
        self.__slots__ = [f[0] for f in fields]
        self._slot_types = [f[1] for f in fields]
        for name, unused, value in fields:
            setattr(self, name, value)


def image(encoding, data, endian=False, width=1, height=1, step=None):
    return Message('sensor_msgs/Image', [
        ('encoding', 'string', encoding), ('width', 'uint32', width),
        ('height', 'uint32', height), ('step', 'uint32', len(data) if step is None else step),
        ('is_bigendian', 'uint8', endian), ('data', 'uint8[]', data)])


class FormattingTests(unittest.TestCase):
    def test_calibration_array_visible(self):
        msg = Message('sensor_msgs/CameraInfo', [('K', 'float64[9]', list(range(9)))])
        self.assertIn('K[8]: 8', sample.message_lines(msg))

    def test_binary_not_dumped(self):
        lines = sample.message_lines(image('mono8', b'\x07' * 1000))
        self.assertTrue(any('1000 bytes; not dumped' in line for line in lines))

    def test_array_preview_limited(self):
        msg = Message('test/Array', [('data', 'float32[]', list(range(10000)))])
        self.assertEqual(len(sample.message_lines(msg)), 17)

    def test_nested_settings_visible(self):
        param = Message('test/Param', [('name', 'string', 'quality'), ('value', 'int32', 80)])
        msg = Message('test/Config', [('ints', 'test/Param[]', [param])])
        self.assertIn('ints[0].value: 80', sample.message_lines(msg))

    def test_depth_endianness(self):
        for big, code in [(True, '>H'), (False, '<H')]:
            lines = sample.image_samples(image('16UC1', struct.pack(code, 1234), big))
            self.assertIn('pixel(0,0) 16UC1 = (1234,)', lines)

    def test_rgb_stride(self):
        data = bytes(bytearray([1, 2, 3, 0, 4, 5, 6, 0]))
        lines = sample.image_samples(image('rgb8', data, height=2, step=4))
        self.assertIn('pixel(0,1) rgb8 = (4, 5, 6)', lines)

    def test_short_buffer(self):
        self.assertIn('[Image buffer too short for declared dimensions/stride]',
                      sample.image_samples(image('32FC1', b'\x00')))

    def test_nan_depth_retained(self):
        lines = sample.image_samples(image('32FC1', struct.pack('<f', float('nan'))))
        self.assertTrue(any('(nan,)' in line for line in lines))

    def test_scan_filters_invalid_and_bounds(self):
        msg = Message('sensor_msgs/LaserScan', [
            ('ranges', 'float32[]', [0, 1.2, float('inf'), float('nan'), 10, 2]),
            ('range_min', 'float32', 0.1), ('range_max', 'float32', 5),
            ('angle_min', 'float32', -1), ('angle_increment', 'float32', 0.2)])
        lines = sample.scan_summary(msg)
        self.assertIn('within declared bounds: 2.', lines[0])
        self.assertIn('1.2000 / 2.0000 metres', lines[1])

    def test_map_counts(self):
        msg = Message('nav_msgs/OccupancyGrid', [('data', 'int8[]', [-1, 0, 100, 50])])
        self.assertIn('unknown(-1)=1, zero occupancy=1, positive occupancy=2', sample.payload_lines(msg)[0])


if __name__ == '__main__':
    unittest.main()
