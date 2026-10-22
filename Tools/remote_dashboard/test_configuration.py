"""Ordinary settings stay bounded and cannot activate ROS, motion or network hosts."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import configuration
import server


class ConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.value = {'schema_version': 1, 'profiles': {'preview': {'port': 8765, 'fps': 3}, 'robot': {'fps': 3}}}

    def test_defaults_and_existing_cli_options(self):
        args = server.parse_args([])
        self.assertEqual((args.port, args.fps, args.ros, args.drive), (8765, 3, False, False))
        self.assertEqual(server.parse_args(['--port', '9877', '--fps', '2']).port, 9877)

    def test_profile_and_explicit_cli_precedence(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'config.json'
            self.value['profiles']['preview'].update(port=9879, fps=1)
            self.value['profiles']['robot']['fps'] = 4
            path.write_text(json.dumps(self.value))
            args = server.parse_args(['--config', str(path)])
            self.assertEqual((args.port,args.fps,args.ros,args.drive), (9879,1,False,False))
            args = server.parse_args(['--config',str(path),'--ros','--fps','2'])
            self.assertEqual((args.port,args.fps,args.drive),(8765,2,False))

    def test_unknown_protected_and_missing_fields_rejected(self):
        for field in ('speed', 'drive', 'host', 'topic', 'command', 'password'):
            value = copy.deepcopy(self.value);value['profiles']['robot'][field] = True
            with self.assertRaises(ValueError):configuration.validate(value)
        del self.value['profiles']['preview']['port']
        with self.assertRaises(ValueError):configuration.validate(self.value)

    def test_invalid_numeric_types_ranges_and_versions(self):
        for field, values in [('port', [True, '8765', 2.5, 1023, 65536]),
                              ('fps', [True, '3', 0, 6, float('nan'), float('inf'), 10**1000])]:
            for number in values:
                value=copy.deepcopy(self.value);value['profiles']['preview'][field]=number
                with self.assertRaises(ValueError):configuration.validate(value)
        self.value['schema_version']=True
        with self.assertRaises(ValueError):configuration.validate(self.value)

    def test_duplicate_oversized_and_missing_file_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'config.json'
            for text in ('{"schema_version":1,"schema_version":1}', ' '*8193):
                path.write_text(text)
                with self.assertRaises(ValueError):configuration.load(path)
            with self.assertRaises(OSError):configuration.load(Path(folder)/'absent')

    def test_bad_configuration_exits_before_ros_or_server(self):
        with mock.patch.object(server,'RosReader') as reader, mock.patch.object(server,'LocalServer') as http:
            with self.assertRaises(SystemExit):server.main(['--ros','--config','not_present_config.json'])
            reader.assert_not_called();http.assert_not_called()


if __name__=='__main__':unittest.main()
