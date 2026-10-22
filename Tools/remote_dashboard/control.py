"""Driving-interface rehearsal only. There is deliberately no motor output."""
from __future__ import print_function

import ctypes
import os
import threading
import time
import uuid


def monotonic_clock():
    if hasattr(time, 'monotonic'):
        return time.monotonic
    # Python 2.7 on the robot: do not use adjustable wall time for a lease.
    if os.name != 'posix':
        raise RuntimeError('A monotonic clock is required; use Python 3 here.')
    class Timespec(ctypes.Structure):
        _fields_ = [('seconds', ctypes.c_long), ('nanoseconds', ctypes.c_long)]
    library = ctypes.CDLL('librt.so.1', use_errno=True)
    gettime = library.clock_gettime
    gettime.argtypes = [ctypes.c_int, ctypes.POINTER(Timespec)]
    gettime.restype = ctypes.c_int
    def clock():
        value = Timespec()
        if gettime(1, ctypes.byref(value)) != 0:
            raise RuntimeError('CLOCK_MONOTONIC failed')
        return value.seconds + value.nanoseconds / 1000000000.0
    clock()
    return clock


ACTIONS = frozenset(('neutral', 'forward', 'forward_left', 'forward_right',
                     'reverse', 'reverse_left', 'reverse_right'))


class RehearsalControl(object):
    """Single-owner, expiring intent display. NOT a verified motor watchdog."""
    def __init__(self, clock=None, timeout=0.5, maximum_arm=30.0):
        self.clock = clock or monotonic_clock()
        self.timeout = timeout
        self.maximum_arm = maximum_arm
        self.lock = threading.RLock()
        self.owner = None
        self.generation = None
        self.action = 'neutral'
        self.reason = 'Start disabled'
        self.sequence = -1
        self.last_contact = None
        self.armed_at = None

    def _stop(self, reason):
        self.owner = None
        self.generation = None
        self.action = 'neutral'
        self.reason = reason
        self.sequence = -1
        self.last_contact = None
        self.armed_at = None

    def _expire(self):
        if self.owner is None:
            return
        now = self.clock()
        if now - self.last_contact >= self.timeout:
            self._stop('Rehearsal heartbeat expired')
        elif now - self.armed_at >= self.maximum_arm:
            self._stop('Rehearsal enable period ended')

    def arm(self, owner):
        if not isinstance(owner, str) or len(owner) != 32:
            # HTTP decoding on Python 2 yields unicode, handled at the boundary.
            raise ValueError('Invalid browser identifier')
        try:
            int(owner, 16)
        except ValueError:
            raise ValueError('Invalid browser identifier')
        with self.lock:
            self._expire()
            if self.owner is not None:
                raise ValueError('Another rehearsal is already enabled; stop first')
            self.owner = owner
            self.generation = uuid.uuid4().hex
            self.last_contact = self.armed_at = self.clock()
            self.action = 'neutral'
            self.reason = 'Rehearsal enabled; motors disconnected'
            return self.generation

    def command(self, owner, generation, sequence, action):
        with self.lock:
            self._expire()
            if self.owner is None or owner != self.owner or generation != self.generation:
                raise ValueError('Rehearsal is disabled or belongs to another browser')
            if type(sequence) is not int or sequence <= self.sequence or sequence > 2147483647:
                raise ValueError('Old or invalid sequence')
            if action not in ACTIONS:
                raise ValueError('Unsupported action: no sideways or in-place turns')
            self.sequence = sequence
            self.action = action
            self.last_contact = self.clock()
            return self.snapshot()

    def stop(self, reason='Stopped by operator'):
        with self.lock:
            self._stop(reason)

    def snapshot(self):
        with self.lock:
            self._expire()
            return {'armed': self.owner is not None, 'owner': self.owner,
                    'action': self.action, 'reason': self.reason,
                    'motor_output': False, 'timeout_ms': int(self.timeout * 1000)}
