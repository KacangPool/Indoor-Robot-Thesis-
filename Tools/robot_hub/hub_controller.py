"""Explicit setup orchestration over an injected connection interface.

No credentials, sockets or UI objects are created on import. Fake connections
can exercise the same workflow without accessing the robot.
"""
from pathlib import Path
import threading
import time
from agent import VERSION
from runtime_bundle import local_manifest


class HubController:
    """Only explicitly requested setup/check operations; no auto fault restart."""
    def __init__(self, connection, source, log=lambda text: None, cancelled=None, update=lambda status: None, progress=lambda phase: None):
        self.connection, self.source, self.log = connection, Path(source), log
        self.cancelled = cancelled or threading.Event()
        self.update = update
        self.progress = progress
        self.manifest = local_manifest(self.source)
        self.last = None
        self.url = None

    def check(self):
        self.last = self.connection.rpc('status')
        self.update(self.last)
        return self.last

    def prepare(self):
        self.progress('Checking existing robot services')
        status = self.check()
        self._ensure('camera')
        status = self.check()
        if self.cancelled.is_set():
            raise RuntimeError('Setup cancelled before runtime update')
        if not status['runtime_ok'] or status.get('installed_bundle') != self.manifest['bundle_id']:
            self.log('Installing verified dashboard v' + VERSION + ' into personal trial folder; original viewer stays unchanged.')
            self.progress('Verifying and updating personal dashboard')
            self.connection.install_runtime(self.source, self.manifest)
        elif (status.get('dashboard') or {}).get('version') not in (None, VERSION):
            raise RuntimeError('Files match but running dashboard is old. Stop it normally before retrying; no blind restart.')
        for service in ('lidar', 'base', 'dashboard'):
            self._ensure(service)
        status = self.check()
        dashboard = status.get('dashboard') or {}
        if dashboard.get('version') != VERSION:
            raise RuntimeError('Running dashboard version differs from v' + VERSION + '; controls were not opened')
        self.progress('Opening private dashboard tunnel')
        self.url = self.connection.ensure_tunnel(dashboard['boot_id'])
        self.log('Tunnel ready. Setup never arms or sends a motion request; use the dashboard Enable once.')
        return status

    def _ensure(self, service):
        self.progress('Checking / starting '+service)
        if self.cancelled.is_set():
            raise RuntimeError('Setup cancelled; no further services started. Inspect existing service state.')
        result = self.connection.rpc('start', service)
        self.log(service + ': ' + result['action'])
        deadline = time.monotonic() + (55 if service == 'camera' else 20)
        while True:
            if self.cancelled.is_set():
                raise RuntimeError('Setup cancelled; services already started remain visible in checks.')
            status = self.check()
            phase = status['services'][service]
            if phase == 'ready': break
            if phase in ('partial', 'conflict') and not status.get('owned', {}).get(service, {}).get('alive'):
                raise RuntimeError(service + ' has partial/conflicting external state; no duplicate started. Inspect logs.')
            if time.monotonic() >= deadline:
                raise RuntimeError(service + ' did not become ready. No automatic restart; inspect service log.')
            self.cancelled.wait(.5)
