"""Encrypted SSH integration against a fake localhost peer. Never a robot."""
import json
from pathlib import Path
import socket
import socketserver
import tempfile
import threading
import unittest
from unittest import mock
from urllib.request import urlopen

import paramiko
import connection


class Peer(paramiko.ServerInterface):
    def __init__(self):
        self.commands = {}
        self.destinations = {}
        self.condition = threading.Condition()

    def check_auth_password(self, username, password):
        return paramiko.AUTH_SUCCESSFUL if (username, password) == ('wheeltec', 'test-only') else paramiko.AUTH_FAILED

    def get_allowed_auths(self, username):
        return 'password'

    def check_channel_request(self, kind, chanid):
        return paramiko.OPEN_SUCCEEDED if kind == 'session' else paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_exec_request(self, channel, command):
        with self.condition:
            self.commands[channel.get_id()] = command.decode()
            self.condition.notify_all()
        return True

    def check_channel_direct_tcpip_request(self, chanid, origin, destination):
        self.destinations[chanid] = destination
        return paramiko.OPEN_SUCCEEDED if destination == ('127.0.0.1', 8765) else paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED


class FakeSSH:
    def __init__(self):
        self.key = paramiko.RSAKey.generate(2048)
        self.socket = socket.socket()
        self.socket.bind(('127.0.0.1', 0))
        self.socket.listen(2)
        self.socket.settimeout(.2)
        self.port = self.socket.getsockname()[1]
        self.peer = Peer()
        self.stopped = threading.Event()
        self.transport = None
        self.thread = threading.Thread(target=self.serve, daemon=True)
        self.thread.start()

    def serve(self):
        try:
            while not self.stopped.is_set():
                try: stream, _ = self.socket.accept(); break
                except socket.timeout: continue
            else: return
            self.transport = paramiko.Transport(stream)
            self.transport.add_server_key(self.key)
            self.transport.start_server(server=self.peer)
            while not self.stopped.is_set() and self.transport.is_active():
                channel = self.transport.accept(.2)
                if channel is not None:
                    threading.Thread(target=self.reply, args=(channel,), daemon=True).start()
        except (EOFError, OSError, paramiko.SSHException):
            pass

    def reply(self, channel):
        try:
            if channel.get_id() in self.peer.destinations:
                channel.settimeout(3)
                request = b''
                while b'\r\n\r\n' not in request:
                    part = channel.recv(8192)
                    if not part: return
                    request += part
                body = b'{"boot_id":"fake-local-peer"}'
                channel.sendall(b'HTTP/1.1 200 OK\r\nConnection: close\r\nContent-Length: ' + str(len(body)).encode() + b'\r\n\r\n' + body)
            else:
                with self.peer.condition:
                    self.peer.condition.wait_for(lambda: channel.get_id() in self.peer.commands, 3)
                channel.sendall(b'FAHAD_HUB_JSON:{"ok":true,"result":{"fake":true}}\n')
                channel.send_exit_status(0)
        except (EOFError, OSError):
            pass
        finally:
            channel.close()

    def close(self):
        self.stopped.set()
        if self.transport: self.transport.close()
        self.socket.close()
        self.thread.join(2)


class EncryptedLoopback(unittest.TestCase):
    def setUp(self):
        self.peer = FakeSSH()
        self.temp = tempfile.TemporaryDirectory()
        self.known = Path(self.temp.name) / 'known_hosts'
        self.known.write_text('[127.0.0.1]:%s %s %s\n' % (self.peer.port, self.peer.key.get_name(), self.peer.key.get_base64()))
        self.robot = connection.RobotConnection('127.0.0.1', self.peer.port, self.known)

    def tearDown(self):
        self.robot.close()
        self.peer.close()
        self.temp.cleanup()

    def test_verified_ssh_rpc_and_internal_tunnel(self):
        self.robot.connect('test-only')
        self.assertEqual(self.robot.rpc('status'), {'fake': True})
        command = next(iter(self.peer.peer.commands.values()))
        self.assertIn('agent.py status', command)
        self.assertNotIn('test-only', command)
        real_server = socketserver.ThreadingTCPServer
        class EphemeralServer(real_server):
            def __init__(self, address, handler):
                super().__init__(('127.0.0.1', 0), handler)
        # Avoid touching any real laptop listener on 8765; use ephemeral fake peer only.
        with mock.patch.object(connection, 'urlopen', side_effect=OSError('test isolation')), mock.patch.object(connection.socketserver, 'ThreadingTCPServer', EphemeralServer):
            self.robot.ensure_tunnel('fake-local-peer')
        address = self.robot.tunnel.server_address
        with urlopen('http://127.0.0.1:%s/api/status' % address[1], timeout=5) as response:
            self.assertEqual(json.load(response), {'boot_id': 'fake-local-peer'})
        self.assertEqual(list(self.peer.peer.destinations.values()), [('127.0.0.1', 8765)])
        self.robot.close()
        self.assertIsNone(self.robot.client)
        self.assertIsNone(self.robot.tunnel)

    def test_unknown_host_key_not_accepted(self):
        self.known.write_text('')
        with self.assertRaisesRegex(RuntimeError, 'connection/authentication failed'):
            self.robot.connect('test-only')
        self.assertEqual(self.known.read_text(), '')

    def test_changed_host_key_not_overwritten(self):
        key = paramiko.RSAKey.generate(2048)
        saved = '[127.0.0.1]:%s %s %s\n' % (self.peer.port, key.get_name(), key.get_base64())
        self.known.write_text(saved)
        with self.assertRaisesRegex(RuntimeError, 'identity changed'):
            self.robot.connect('test-only')
        self.assertEqual(self.known.read_text(), saved)


if __name__ == '__main__': unittest.main()
