"""The checker must retain failures/skips and never hide a missing runtime."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import quality_check


class QualityTests(unittest.TestCase):
    def test_missing_runtime_is_blocked_and_installs_nothing(self):
        with tempfile.TemporaryDirectory() as folder, mock.patch.object(quality_check.subprocess,'run') as run:
            result=quality_check.run_command('missing',[None],Path(folder))
            self.assertEqual(result['status'],'blocked');run.assert_not_called()

    def test_nonzero_and_timeout_remain_failures(self):
        with tempfile.TemporaryDirectory() as folder:
            result=quality_check.run_command('failed',[sys.executable,'-c','raise SystemExit(7)'],Path(folder))
            self.assertEqual((result['status'],result['returncode']),('fail',7))
            with mock.patch.object(quality_check.subprocess,'run',side_effect=subprocess.TimeoutExpired('test',1)) as run:
                result=quality_check.run_command('timed_out',['unused'],Path(folder),timeout=1)
            self.assertEqual(result['status'],'timeout');run.assert_called_once()

    def test_worker_reports_test_errors_and_skips_separately(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            # Tiny generated test fixture; never imports or executes project entry points.
            (root/'test_fixture.py').write_text('import unittest\nclass Example(unittest.TestCase):\n def test_error(self): raise RuntimeError("intentional fixture error")\n @unittest.skip("intentional fixture skip")\n def test_skip(self): pass\n')
            path=root/'result.json'
            value=quality_check.run_command('worker',[sys.executable,str(quality_check.ROOT/'Tools/quality_suite.py'),
                '--start',str(root),'--result',str(path)],root,result_file=path)
            self.assertEqual(value['status'],'fail')
            self.assertEqual(value['unittest']['tests_run'],2)
            self.assertEqual(len(value['unittest']['errors']),1);self.assertEqual(len(value['unittest']['skipped']),1)

    def test_missing_result_cannot_be_reported_as_success(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            value=quality_check.run_command('no_report',[sys.executable,'-c','pass'],root,result_file=root/'absent.json')
            self.assertEqual(value['status'],'fail')

    def test_corrupt_worker_report_is_failure_not_a_crash(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);path=root/'result.json';path.write_text('not json')
            value=quality_check.run_command('corrupt',[sys.executable,'-c','pass'],root,result_file=path)
            self.assertEqual(value['status'],'fail')

    def test_empty_suite_cannot_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);path=root/'result.json'
            value=quality_check.run_command('empty',[sys.executable,str(quality_check.ROOT/'Tools/quality_suite.py'),
                '--start',str(root),'--result',str(path)],root,result_file=path)
            self.assertEqual(value['status'],'fail');self.assertEqual(value['unittest']['tests_run'],0)

    def test_report_records_nonpassing_checks_and_skip_details(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            result=quality_check.write_summary(root,[{'name':'missing','status':'blocked','reason':'No Node'}],{})
            self.assertEqual(result,1)
            value=json.loads((root/'summary.json').read_text())
            self.assertEqual(value['overall'],'attention_required');self.assertIn('No Node',(root/'summary.md').read_text())

    def test_static_checks_do_not_import_ros_or_models(self):
        with mock.patch.dict(sys.modules,{}):
            self.assertGreater(quality_check.static_checks(),20)
        self.assertNotIn('rospy',sys.modules);self.assertNotIn('torch',sys.modules)

    def test_source_inventory_hashes_only_listed_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'source.py').write_text('value=1\n');(root/'private.key').write_text('excluded')
            result=mock.Mock(returncode=0,stdout=b'source.py\0')
            with mock.patch.object(quality_check.subprocess,'run',return_value=result):
                files=quality_check.source_inventory('fake_git',root)
            self.assertEqual(set(files),{'source.py'});self.assertEqual(len(files['source.py']),64)


if __name__=='__main__':unittest.main()
