"""Windows hub SSH, private SFTP update and loopback-only tunnel.

No passwords/config/host keys are written. No automatic host-key acceptance.
Paramiko import is lazy so offline/demo/tests do not need SSH dependencies.
"""
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import shlex
import socket
import socketserver
import stat
import threading
import time
from urllib.request import urlopen
import uuid

from agent import VERSION, RUNTIME_FILES, bundle_id

REMOTE = '/home/wheeltec/fahad'
AGENT = REMOTE + '/robot_hub/agent.py'


from runtime_bundle import local_manifest


class RobotConnection:
    def __init__(self, host='192.168.0.100', ssh_port=22, known_hosts=None):
        address = ipaddress.ip_address(host)
        if address.version != 4 or not address.is_private:
            raise ValueError('Use the robot local IPv4 address, normally 192.168.0.100')
        self.host, self.client = host, None
        if type(ssh_port) is not int or not 1 <= ssh_port <= 65535:
            raise ValueError('Invalid SSH port')
        self.ssh_port, self.known_hosts = ssh_port, known_hosts
        self.tunnel = self.tunnel_thread = None
        self.tunnel_stop = threading.Event()
        self.reused_tunnel = False

    def connect(self, password):
        import paramiko
        known = Path(self.known_hosts) if self.known_hosts else Path.home() / '.ssh' / 'known_hosts'
        if not known.is_file():
            raise RuntimeError('No saved SSH host identity. Verify the robot once using normal Windows SSH, then retry.')
        client = paramiko.SSHClient()
        client.load_system_host_keys(str(known))
        client.set_missing_host_key_policy(paramiko.RejectPolicy())
        try:
            client.connect(self.host, port=self.ssh_port, username='wheeltec', password=password or None,
                           allow_agent=not bool(password), look_for_keys=not bool(password), timeout=6,
                           banner_timeout=6, auth_timeout=12)
            client.get_transport().set_keepalive(5)
        except Exception as exc:
            client.close()
            if isinstance(exc, paramiko.BadHostKeyException):
                raise RuntimeError('SSH host identity changed. Stop and verify the robot; saved keys were not overwritten.') from None
            raise RuntimeError('SSH connection/authentication failed (' + type(exc).__name__ + '). Check robot Wi-Fi, saved host identity and login.') from None
        self.client = client

    def rpc(self, action, value=None):
        choices = {'status', 'start', 'logs', 'stop-drive', 'prepare-update', 'deploy'}
        if action not in choices:
            raise ValueError('Unknown robot action')
        if action in ('start', 'logs') and value not in ('camera', 'lidar', 'base', 'dashboard'):
            raise ValueError('Unknown fixed service')
        if action == 'deploy' and (not isinstance(value, str) or len(value) != 32 or any(c not in '0123456789abcdef' for c in value)):
            raise ValueError('Invalid bundle identity')
        if action not in ('start', 'logs', 'deploy') and value is not None:
            raise ValueError('Unexpected argument')
        if not self.client or not self.client.get_transport().is_active():
            raise RuntimeError('SSH disconnected; reconnect deliberately. No services automatically restarted.')
        argv = ['python', AGENT, action] + ([value] if value else [])
        inner = 'source /home/wheeltec/wheeltec_robot/devel/setup.bash && exec ' + ' '.join(shlex.quote(x) for x in argv)
        command = 'bash -lc ' + shlex.quote(inner)
        stdin, stdout, stderr = self.client.exec_command(command, timeout=18)
        stdin.close()
        channel, output, errors = stdout.channel, bytearray(), bytearray()
        deadline = time.monotonic() + 18
        while True:
            while channel.recv_ready(): output.extend(channel.recv(16384))
            while channel.recv_stderr_ready(): errors.extend(channel.recv_stderr(16384))
            if len(output) + len(errors) > 262144:
                channel.close()
                raise RuntimeError('Robot response exceeded bounded size')
            if channel.exit_status_ready() and not channel.recv_ready() and not channel.recv_stderr_ready():
                break
            if time.monotonic() >= deadline:
                channel.close()
                raise RuntimeError('Robot check timed out; no automatic restart')
            time.sleep(.01)
        code = channel.recv_exit_status()
        channel.close()
        stdout.close()
        stderr.close()
        lines = output.decode('utf8', 'replace').splitlines()
        protocol = [line[len('FAHAD_HUB_JSON:'):] for line in lines if line.startswith('FAHAD_HUB_JSON:')]
        if code != 0 or not protocol:
            raise RuntimeError('Robot helper unavailable: ' + errors.decode('utf8', 'replace')[-1200:])
        response = json.loads(protocol[-1])
        if not response.get('ok'):
            raise RuntimeError(response.get('error', 'Robot refused action'))
        return response['result']

    @staticmethod
    def _mkdir(sftp, path):
        parts = path.strip('/').split('/')
        current = ''
        for part in parts:
            current += '/' + part
            try:
                mode = sftp.lstat(current).st_mode
                if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
                    raise RuntimeError('Remote path is not an ordinary directory: ' + current)
            except FileNotFoundError:
                if not current.startswith(REMOTE + '/'):
                    raise RuntimeError('Robot personal directory is missing')
                sftp.mkdir(current, mode=0o700)

    @staticmethod
    def _upload(sftp, data, target):
        if not target.startswith(REMOTE + '/robot_hub/'):
            raise RuntimeError('Upload outside personal hub directory refused')
        RobotConnection._mkdir(sftp, target.rsplit('/', 1)[0])
        temporary = target + '.upload-' + uuid.uuid4().hex
        with sftp.file(temporary, 'wb') as output:
            output.write(data)
        sftp.chmod(temporary, 0o600)
        # OpenSSH supports this atomic replacement extension. On unsupported
        # servers fail rather than unlinking an existing destination first.
        sftp.posix_rename(temporary, target)

    def install_agent(self):
        with self.client.open_sftp() as sftp:
            sftp.get_channel().settimeout(10)
            self._upload(sftp, Path(__file__).with_name('agent.py').read_bytes(), AGENT)

    def install_runtime(self, source, manifest):
        self.rpc('prepare-update')
        identity = uuid.uuid4().hex
        stage = REMOTE + '/robot_hub/staging/' + identity
        with self.client.open_sftp() as sftp:
            sftp.get_channel().settimeout(10)
            for name in RUNTIME_FILES:
                self._upload(sftp, (Path(source) / name).read_bytes(), stage + '/' + name)
            self._upload(sftp, json.dumps(manifest, sort_keys=True).encode('utf8'), stage + '/manifest.json')
        result = self.rpc('deploy', identity)
        if not result.get('verified'):
            raise RuntimeError('Installed runtime checksum verification failed; not starting services')
        return result

    def ensure_tunnel(self, expected_boot):
        if self.tunnel:
            return 'http://127.0.0.1:8765/'
        try:
            with urlopen('http://127.0.0.1:8765/api/status', timeout=1) as response:
                state = json.loads(response.read(262145).decode('utf8'))
            if state.get('boot_id') == expected_boot:
                self.reused_tunnel = True
                return 'http://127.0.0.1:8765/'
        except Exception:
            pass
        connection = self
        slots = threading.BoundedSemaphore(16)
        class Handler(socketserver.BaseRequestHandler):
            def handle(self):
                if not slots.acquire(False): return
                channel = None
                done = threading.Event()
                try:
                    transport = connection.client.get_transport()
                    channel = transport.open_channel('direct-tcpip', ('127.0.0.1',8765), self.client_address, timeout=5)
                    channel.settimeout(.5)
                    self.request.settimeout(.5)
                    def outgoing():
                        try:
                            while not done.is_set() and not connection.tunnel_stop.is_set():
                                try: data = self.request.recv(65536)
                                except socket.timeout: continue
                                if not data: break
                                channel.sendall(data)
                        except Exception:
                            pass
                        finally:
                            done.set()
                    thread = threading.Thread(target=outgoing, daemon=True)
                    thread.start()
                    while not done.is_set() and not connection.tunnel_stop.is_set():
                        try: data = channel.recv(65536)
                        except socket.timeout: continue
                        if not data: break
                        self.request.sendall(data)
                except Exception:
                    pass
                finally:
                    done.set()
                    if channel: channel.close()
                    slots.release()
        class Tunnel(socketserver.ThreadingTCPServer):
            allow_reuse_address = False
            daemon_threads = True
        try:
            self.tunnel = Tunnel(('127.0.0.1',8765), Handler)
        except OSError:
            raise RuntimeError('Laptop port 8765 belongs to a different/unverified listener. It was not killed.')
        self.tunnel_stop.clear()
        self.tunnel_thread = threading.Thread(target=self.tunnel.serve_forever, daemon=True)
        self.tunnel_thread.start()
        return 'http://127.0.0.1:8765/'

    def close(self):
        self.tunnel_stop.set()
        if self.tunnel:
            self.tunnel.shutdown()
            self.tunnel.server_close()
            self.tunnel = None
        if self.client:
            self.client.close()
            self.client = None


# Compatibility export: existing launchers/imports keep working.
from hub_controller import HubController
