import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fahad_core.inventory import catalogue, discover_files, xml_root
import robot_inventory


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value, encoding='utf8')
        return path

    def test_source_only_extracts_declarations_not_parameter_secrets(self):
        self.write('pkg/package.xml', '<package><name>demo</name><version>1</version><exec_depend>roscpp</exec_depend></package>')
        self.write('pkg/a.launch', '<launch><node pkg="demo" type="driver" args="PRIVATE"/><param name="password" value="PRIVATE"/></launch>')
        result = catalogue(self.root)
        self.assertEqual(result['packages'][0]['dependencies'], ['roscpp'])
        self.assertEqual(result['launches'][0]['nodes'], [{'package': 'demo', 'type': 'driver'}])
        self.assertNotIn('PRIVATE', str(result))
        self.assertEqual(result['evidence'], 'source_files_only')

    def test_unsafe_and_invalid_xml_recorded_without_raw_error(self):
        self.write('a/package.xml', '<!DOCTYPE x [<!ENTITY y "SECRET">]><package/>')
        self.write('b/b.launch', '<launch>')
        result = catalogue(self.root)
        self.assertEqual(len(result['issues']), 2)
        self.assertNotIn('SECRET', str(result))

    def test_traversal_limit_and_build_exclusion(self):
        self.write('build/package.xml', '<package/>')
        self.write('a.txt', 'x')
        self.assertEqual(len(list(discover_files(self.root, 1))), 1)
        self.write('b.txt', 'x')
        with self.assertRaises(ValueError):
            list(discover_files(self.root, 1))

    def test_oversize_xml_refused(self):
        path = self.write('big.launch', 'x' * (512 * 1024 + 1))
        with self.assertRaises(ValueError):
            xml_root(path)

    def test_import_does_not_launch_processes(self):
        with patch('subprocess.Popen', side_effect=AssertionError('must not launch')):
            spec = importlib.util.spec_from_file_location('inventory_import_test', robot_inventory.__file__)
            spec.loader.exec_module(importlib.util.module_from_spec(spec))

    def test_report_refuses_overwrite(self):
        path = self.write('report.json', 'original')
        with self.assertRaises(SystemExit):
            robot_inventory.main(['--source-root', str(self.root), '--output', str(path)])
        self.assertEqual(path.read_text(), 'original')

    def test_no_live_checks_in_source_mode(self):
        with patch.object(robot_inventory, 'live_inventory', side_effect=AssertionError('not requested')):
            self.assertEqual(robot_inventory.main(['--source-root', str(self.root), '--output', str(self.root/'report.json')]), 0)

    def test_missing_command_explicit(self):
        with patch('shutil.which', return_value=None):
            self.assertEqual(robot_inventory.observe(['rospack', 'list'])['status'], 'unavailable')


if __name__ == '__main__':
    unittest.main()
