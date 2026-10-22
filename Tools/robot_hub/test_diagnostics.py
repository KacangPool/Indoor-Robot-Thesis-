"""Allowlisted diagnostics, bounded logs and UI export; no real UI/robot access."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import agent
import diagnostics
import hub


class DiagnosticTests(unittest.TestCase):
    def status(self):
        return {'agent_version': agent.VERSION, 'services': {'lidar': 'ready'},
                'graph': {'reachable': True}, 'dashboard': {'version': agent.VERSION,
                    'cameras': {'rgb': {'available': True, 'age_s': .1}},
                    'scan': {'state': 'waiting_messages', 'available': False,
                             'publisher_connections': 1, 'messages_received': 0}}}

    def test_registration_without_messages_has_specific_issue(self):
        result=diagnostics.report(self.status(),snapshot_age_s=0)
        self.assertEqual(result['services']['lidar'],'ready')
        self.assertIn('SCAN_CONNECTION_WITHOUT_RECEIVED_MESSAGES',result['issues'])
        self.assertFalse(result['scan']['available'])

    def test_old_and_unknown_snapshots_not_called_live(self):
        for age in (None, 11, -1, float('nan')):
            value=diagnostics.report(self.status(),snapshot_age_s=age)
            self.assertIn('STATUS_AGE_UNKNOWN_OR_OLD',value['issues'])
            self.assertEqual(value['evidence'],'last_checked_snapshot_not_a_new_probe')
            json.dumps(value,allow_nan=False)

    def test_secret_fields_and_raw_logs_never_exported(self):
        status=self.status();secret='DO_NOT_EXPORT_THIS_VALUE'
        status.update(password=secret,key=secret,graph={'reachable':True,'nodes':[secret]},raw_log=secret)
        status['dashboard']['control']={'owner':secret,'generation':secret,'last_disable':{'reason':secret}}
        status['owned']={'camera':{'alive':True,'pid':123,'argv':[secret]}}
        result=diagnostics.report(status,run_id=secret,events=[{'event':'task_failed','password':secret,'elapsed_s':2}])
        self.assertNotIn(secret,json.dumps(result))
        self.assertEqual(result['owned_processes']['camera']['pid'],123)

    def test_invalid_numeric_and_state_fields_are_not_copied(self):
        status=self.status();status['dashboard']['scan'].update(arrival_rate_hz=float('inf'),state='TOKEN')
        result=diagnostics.report(status)
        self.assertIsNone(result['scan']['arrival_rate_hz']);self.assertEqual(result['scan']['state'],'unknown')
        self.assertEqual(diagnostics.clean_event({'event':[]})['event'],'unknown')
        self.assertIsNone(diagnostics.number(10**1000))
        self.assertIn('NO_RECENT_RGB_REPORTED',diagnostics.report({'dashboard':'invalid'})['issues'])

    def test_event_memory_and_file_rotation_are_bounded(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'events.jsonl'
            logger=diagnostics.SessionLog(lambda:100,path)
            try:
                for index in range(1800):logger.record('status_checked')
                self.assertEqual(len(logger.events),200)
                with self.assertRaises(ValueError):logger.record('arbitrary raw text')
            finally:logger.close()
            files=list(Path(folder).glob('events.jsonl*'))
            self.assertGreater(len(files),1);self.assertLessEqual(len(files),3)
            self.assertTrue(all(item.stat().st_size<=262144 for item in files))
            for line in path.read_text(encoding='utf8').splitlines():
                value=json.loads(line);self.assertEqual(value['component'],'robot_hub')

    def test_ui_save_uses_sanitized_existing_snapshot_without_rpc(self):
        app=hub.App.__new__(hub.App);app.last=self.status();app.note=mock.Mock();app.connection=mock.Mock()
        app.last['password']='DO_NOT_EXPORT';app.demo=True
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'report.json'
            with mock.patch.object(hub.filedialog,'asksaveasfilename',return_value=str(path)):
                app.save_report()
            value=json.loads(path.read_text());self.assertEqual(value['evidence'],'demo_snapshot')
            self.assertNotIn('DO_NOT_EXPORT',path.read_text())
        app.connection.rpc.assert_not_called()

    def test_runtime_inventory_is_read_only_and_missing_disk_data_is_explicit(self):
        with mock.patch.object(agent.os,'statvfs',create=True,side_effect=OSError):
            value=agent.runtime_summary('unavailable')
        self.assertIsNone(value['disk_free_bytes']);self.assertIsInstance(value['python_major'],int)


if __name__=='__main__':unittest.main()
