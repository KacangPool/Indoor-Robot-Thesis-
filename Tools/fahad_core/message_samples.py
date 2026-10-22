"""Bounded formatting/decoding; no ROS startup or import-time subscriptions.

The PointCloud2 payload branch lazily imports the existing ROS decoder.
"""
import math
import struct

ARRAY_PREVIEW = 16
LINE_LIMIT = 240


def finite(value):
    return not math.isnan(value) and not math.isinf(value)


def message_lines(message):
    """Show nested fields, small arrays and binary sizes, with explicit limits."""
    lines = []

    def visit(value, kind, path, depth):
        if len(lines) >= LINE_LIMIT:
            return
        if depth > 10:
            lines.append(path + ': [nesting limit]')
        elif '[' in kind:
            count = len(value)
            base = kind.split('[')[0]
            if base in ('uint8', 'char'):
                lines.append('%s: [binary/byte array, %d bytes; not dumped]' % (path, count))
                return
            lines.append('%s: [%d elements; showing first %d]' % (path, count, min(count, ARRAY_PREVIEW)))
            for index in range(min(count, ARRAY_PREVIEW)):
                visit(value[index], base, '%s[%d]' % (path, index), depth + 1)
        elif hasattr(value, '_slot_types'):
            for name, slot_type in zip(value.__slots__, value._slot_types):
                visit(getattr(value, name), slot_type, path + '.' + name if path else name, depth + 1)
        elif kind in ('time', 'duration'):
            lines.append('%s: secs=%s nsecs=%s' % (path, value.secs, value.nsecs))
        else:
            shown = repr(value)
            lines.append('%s: %s' % (path, shown if len(shown) <= 220 else shown[:220] + ' [truncated]'))

    visit(message, getattr(message, '_type', ''), '', 0)
    if len(lines) >= LINE_LIMIT:
        lines.append('[Field preview stopped at %d lines; use definition for complete structure.]' % LINE_LIMIT)
    return lines


def image_samples(message):
    """Decode nine pixels with declared encoding, stride and byte order."""
    formats = {'rgb8': ('BBB', 3), 'bgr8': ('BBB', 3), 'mono8': ('B', 1),
               '16UC1': ('H', 2), 'mono16': ('H', 2), '32FC1': ('f', 4)}
    if message.encoding not in formats:
        return ['[Pixel decoding not implemented for encoding %s]' % message.encoding]
    if message.width < 1 or message.height < 1:
        return ['[Empty image]']
    code, size = formats[message.encoding]
    endian = '>' if message.is_bigendian else '<'
    lines = ['PIXEL EXAMPLES: (x,y) from top-left; nine grid positions, not whole-image statistics.']
    for y in sorted(set([0, message.height // 2, message.height - 1])):
        for x in sorted(set([0, message.width // 2, message.width - 1])):
            offset = y * message.step + x * size
            if offset + size > len(message.data):
                lines.append('[Image buffer too short for declared dimensions/stride]')
                return lines
            values = struct.unpack_from(endian + code, message.data, offset)
            lines.append('pixel(%d,%d) %s = %s' % (x, y, message.encoding, values))
    lines.append('For conventional ROS depth: 16UC1 is mm; 32FC1 is metres. Encoding alone does not prove a depth image. Verify driver/topic semantics. Zero/nonfinite depth is not a usable distance.')
    return lines


def scan_summary(message):
    values = message.ranges
    checked = values[:100000]
    valid = [v for v in checked if finite(v) and message.range_min <= v <= message.range_max]
    lines = ['SCAN: inspected %d/%d rays; finite and within declared bounds: %d.' %
             (len(checked), len(values), len(valid))]
    if valid:
        lines.append('Valid range min/max in inspected rays: %.4f / %.4f metres.' % (min(valid), max(valid)))
    if values:
        for index in sorted(set([0, len(values) // 4, len(values) // 2, 3 * len(values) // 4, len(values) - 1])):
            lines.append('ray[%d]: angle=%.6f rad, range=%s m' %
                         (index, message.angle_min + index * message.angle_increment, values[index]))
    lines.append('These are planar rays, not identified objects; declared bounds are not verified hardware capability.')
    return lines


def payload_lines(message):
    kind = message._type
    if kind == 'sensor_msgs/Image':
        return image_samples(message)
    if kind == 'sensor_msgs/LaserScan':
        return scan_summary(message)
    if kind == 'sensor_msgs/PointCloud2':
        from itertools import islice
        from sensor_msgs import point_cloud2
        names = [field.name for field in message.fields]
        wanted = [name for name in ('x', 'y', 'z', 'rgb', 'rgba', 'intensity') if name in names]
        if not wanted:
            return ['[No supported point fields; inspect fields/offset/datatype metadata.]']
        points = list(islice(point_cloud2.read_points(message, field_names=wanted, skip_nans=False), 8))
        ordered = [(field.name, field.count) for field in sorted(message.fields, key=lambda f: f.offset) if field.name in wanted]
        return ['POINT EXAMPLES: (field,count) order %s; first 8 points (NaN retained); coordinates use header.frame_id. Packed rgb is not a distance.' % ordered, repr(points)]
    if kind == 'nav_msgs/OccupancyGrid':
        values = message.data[:100000]
        return ['GRID: first %d/%d cells: unknown(-1)=%d, zero occupancy=%d, positive occupancy=%d. Values 0..100 are occupancy estimates, not object classes.' %
                (len(values), len(message.data), sum(v == -1 for v in values), sum(v == 0 for v in values), sum(v > 0 for v in values))]
    return []
