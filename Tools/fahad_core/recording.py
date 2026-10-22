"""Bounded image cache, exact frame keys and explicit recording IO helpers.

Importing does not read/write files or start ROS. Callers choose output paths.
"""
import collections
import io
import json
import os


def header_dict(header):
    return {'seq': int(header.seq), 'secs': int(header.stamp.secs),
            'nsecs': int(header.stamp.nsecs), 'frame_id': str(header.frame_id)}


def frame_key(header):
    # Require identical time, sequence and frame, rather than nearest image.
    return (header['secs'], header['nsecs'], header['seq'], header['frame_id'])


class ImageCache(object):
    """Caller holds its lock; bounded references to ROS image messages."""
    def __init__(self, capacity):
        self.capacity = capacity
        self.frames = collections.OrderedDict()

    def put(self, key, message):
        self.frames[key] = message
        while len(self.frames) > self.capacity:
            self.frames.popitem(last=False)

    def get(self, key):
        return self.frames.get(key)

    def latest(self):
        if not self.frames:
            return None
        return self.frames[next(reversed(self.frames))]


def write_json(path, data):
    with io.open(path, 'w', encoding='utf-8') as stream:
        stream.write(json.dumps(data, ensure_ascii=True, indent=2,
                                allow_nan=False) + u'\n')


def append_json(stream, data):
    stream.write(json.dumps(data, ensure_ascii=True, allow_nan=False) + u'\n')
    stream.flush()


def free_megabytes(path):
    # The deployment host is Linux. Return None if this check is unavailable.
    if not hasattr(os, 'statvfs'):
        return None
    stat = os.statvfs(path)
    return stat.f_bavail * stat.f_frsize / float(1024 * 1024)
