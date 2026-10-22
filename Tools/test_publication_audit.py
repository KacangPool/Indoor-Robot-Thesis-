"""Publication audit contracts. Synthetic markers only; no real credentials."""
import unittest
from unittest import mock
import publication_audit as audit


class AuditTests(unittest.TestCase):
    def test_source_allowlist(self):
        for name in ('README.md', 'Tools/test.py', 'Documentation/notes.md',
                     'Tools/remote_dashboard/dashboard_config.json', '.github/workflows/checks.yml', '.github/ci-requirements.txt'):
            self.assertTrue(audit.allowed(name), name)

    def test_data_private_vendor_and_symlink_path_scope_rejected(self):
        for name in ('Tool reports/result.json', 'Sites/fieldnotes/package.json', 'From Robotics Lab/source.py',
                     'Tools/.env', 'Tools/key.pem', 'Tools/logs/result.json', 'Documentation/manual.pdf',
                     'Tools/../private.py', '/Tools/test.py', 'Tools/video.mp4', 'Tools/secrets.json'):
            self.assertFalse(audit.allowed(name), name)

    def test_high_confidence_markers_redacted_to_location(self):
        token = b'gh' + b'p_' + b'A'*36
        result = audit.findings(b'first line\nvalue=' + token)
        self.assertEqual(result, [{'category':'github_classic_token','line':2}])
        self.assertNotIn(token.decode(), str(result))

    def test_ordinary_code_has_no_secret_findings(self):
        self.assertEqual(audit.findings(b'password = None\nkey = uuid.uuid4().hex\n'), [])

    def test_literal_credentials_are_flagged_without_values(self):
        value=b'pass'+b'word = '+b'"' + b'synthetic marker' + b'"'
        result=audit.findings(value)
        self.assertEqual(result[0]['category'],'literal_credential_assignment')
        self.assertNotIn('synthetic marker',str(result))

    def test_audit_deduplicates_blobs_and_rejects_symlinks(self):
        sha='a'*40
        def git(*args, **kwargs):
            if args[0]=='rev-list':return b'commit1\ncommit2\n'
            if args[0]=='ls-tree':return ('100644 blob '+sha+'\tTools/test.py\0'+'120000 blob '+sha+'\tTools/link.py\0').encode()
            return b'normal code\n'
        with mock.patch.object(audit,'git',side_effect=git):value=audit.audit()
        self.assertEqual(value['unique_blobs_checked'],1)
        self.assertEqual(len(value['issues']),2)
        self.assertEqual(value['status'],'attention_required')

    def test_synthetic_exception_is_file_version_specific(self):
        record=next(iter(audit.REVIEWED_FIXTURES))
        self.assertEqual(record[0],'Tools/robot_hub/test_diagnostics.py')
        self.assertNotIn(('Tools/other.py',*record[1:]),audit.REVIEWED_FIXTURES)
        self.assertNotIn((record[0],'b'*40,*record[2:]),audit.REVIEWED_FIXTURES)


if __name__=='__main__':unittest.main()
