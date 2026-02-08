#!/usr/bin/env python3
"""Tests for send.py email module."""
import json
import os
import sys
import tempfile
import unittest
import urllib.request
from unittest import mock

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
skill_dir = os.path.join(parent_dir, 'skill', 'send-email-mailjet', 'scripts')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, skill_dir)
import send
from http_echo_server import (
    clear_captured_request,
    run_server,
)


class TestLoadEnvFile(unittest.TestCase):
    """Tests for load_env_file function."""

    def setUp(self):
        """Clear relevant environment variables before each test."""
        self.env_vars_to_clear = [
            'TEST_VAR', 'TEST_VAR2', 'QUOTED_VAR', 'SINGLE_QUOTED',
            'MAIL_FROM', 'MAIL_TO', 'MAIL_FILES_1'
        ]
        self.original_env = {}
        for var in self.env_vars_to_clear:
            self.original_env[var] = os.environ.pop(var, None)

    def tearDown(self):
        """Restore original environment variables."""
        for var, value in self.original_env.items():
            if value is not None:
                os.environ[var] = value
            else:
                os.environ.pop(var, None)

    def test_load_simple_env_file(self):
        """Test loading simple KEY=VALUE pairs."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write('TEST_VAR=hello\n')
            f.write('TEST_VAR2=world\n')
            env_path = f.name

        try:
            send.load_env_file(env_path)
            self.assertEqual(os.environ.get('TEST_VAR'), 'hello')
            self.assertEqual(os.environ.get('TEST_VAR2'), 'world')
        finally:
            os.unlink(env_path)

    def test_load_quoted_values(self):
        """Test loading values with quotes."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write('QUOTED_VAR="hello world"\n')
            f.write("SINGLE_QUOTED='single quotes'\n")
            env_path = f.name

        try:
            send.load_env_file(env_path)
            self.assertEqual(os.environ.get('QUOTED_VAR'), 'hello world')
            self.assertEqual(os.environ.get('SINGLE_QUOTED'), 'single quotes')
        finally:
            os.unlink(env_path)

    def test_skip_comments_and_empty_lines(self):
        """Test that comments and empty lines are skipped."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write('# This is a comment\n')
            f.write('\n')
            f.write('TEST_VAR=value\n')
            f.write('  # Indented comment\n')
            env_path = f.name

        try:
            send.load_env_file(env_path)
            self.assertEqual(os.environ.get('TEST_VAR'), 'value')
        finally:
            os.unlink(env_path)

    def test_env_vars_take_precedence(self):
        """Test that existing env vars are not overwritten."""
        os.environ['TEST_VAR'] = 'original'
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write('TEST_VAR=from_file\n')
            env_path = f.name

        try:
            send.load_env_file(env_path)
            self.assertEqual(os.environ.get('TEST_VAR'), 'original')
        finally:
            os.unlink(env_path)

    def test_nonexistent_file(self):
        """Test that nonexistent file is handled gracefully."""
        # Should not raise an exception
        send.load_env_file('/nonexistent/path/.env')


class TestGetFilesFromEnv(unittest.TestCase):
    """Tests for get_files_from_env function."""

    def setUp(self):
        """Clear MAIL_FILES_* environment variables."""
        self.original_env = {}
        for i in range(1, 10):
            key = f'MAIL_FILES_{i}'
            self.original_env[key] = os.environ.pop(key, None)

    def tearDown(self):
        """Restore original environment variables."""
        for key, value in self.original_env.items():
            if value is not None:
                os.environ[key] = value
            else:
                os.environ.pop(key, None)

    def test_no_files(self):
        """Test when no MAIL_FILES_* are set."""
        files = send.get_files_from_env()
        self.assertEqual(files, [])

    # def test_single_file(self):
    #     """Test with single MAIL_FILES_1."""
    #     os.environ['MAIL_FILES_1'] = '/path/to/file.pdf'
    #     files = send.get_files_from_env()
    #     self.assertEqual(files, ['/path/to/file.pdf'])

    # def test_multiple_files(self):
    #     """Test with multiple MAIL_FILES_* variables."""
    #     os.environ['MAIL_FILES_1'] = '/path/to/file1.pdf'
    #     os.environ['MAIL_FILES_2'] = '/path/to/file2.epub'
    #     os.environ['MAIL_FILES_3'] = '/path/to/file3.txt'
        
        # files = send.get_files_from_env()
        # self.assertEqual(files, [
        #     '/path/to/file1.pdf',
        #     '/path/to/file2.epub',
        #     '/path/to/file3.txt'
        # ])

    def test_gap_in_numbering(self):
        """Test that gaps in numbering stop the sequence."""
        os.environ['MAIL_FILES_1'] = '/path/to/file1.pdf'
        # MAIL_FILES_2 is not set
        os.environ['MAIL_FILES_3'] = '/path/to/file3.pdf'
        
        files = send.get_files_from_env()
        # Should only get file1 because file2 breaks the sequence
        self.assertEqual(files, ['/path/to/file1.pdf'])


class TestGetContentType(unittest.TestCase):
    """Tests for get_content_type function."""

    def test_supported_extensions(self):
        """Test common file extensions using mimetypes module."""
        test_cases = [
            ('document.md', 'text/markdown'),
            ('document.txt', 'text/plain'),
            ('book.epub', 'application/epub+zip'),
            ('book.fb2', 'application/x-fictionbook+xml'),
            ('document.pdf', 'application/pdf'),
            ('page.html', 'text/html'),
            ('page.htm', 'text/html'),
            ('image.png', 'image/png'),
            ('image.jpg', 'image/jpeg'),
        ]
        for file_path, expected_type in test_cases:
            with self.subTest(file_path=file_path):
                result = send.get_content_type(file_path)
                self.assertEqual(result, expected_type)

    def test_case_insensitive(self):
        """Test that extension matching is case-insensitive."""
        self.assertEqual(send.get_content_type('file.PDF'), 'application/pdf')
        self.assertEqual(send.get_content_type('file.EPUB'), 'application/epub+zip')

    def test_unknown_extension_returns_octet_stream(self):
        """Test that unknown extension returns application/octet-stream."""
        result = send.get_content_type('file.unknownext123')
        self.assertEqual(result, 'application/octet-stream')


class TestCreateAttachment(unittest.TestCase):
    """Tests for create_attachment function."""

    def test_create_attachment_from_file(self):
        """Test creating attachment from a real file."""
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.txt', delete=False
        ) as f:
            f.write('Test content')
            file_path = f.name

        try:
            attachment = send.create_attachment(file_path)
            
            self.assertEqual(attachment['ContentType'], 'text/plain')
            self.assertTrue(attachment['Filename'].endswith('.txt'))
            self.assertEqual(attachment['ContentID'], attachment['Filename'])
            # Base64 encoded 'Test content'
            self.assertIn('Base64Content', attachment)
        finally:
            os.unlink(file_path)

    def test_filename_sanitization(self):
        """Test that filenames with spaces/tabs are sanitized."""
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.txt', delete=False, prefix='test file '
        ) as f:
            f.write('content')
            file_path = f.name

        try:
            attachment = send.create_attachment(file_path)
            # Spaces should be replaced with underscores
            self.assertNotIn(' ', attachment['Filename'])
        finally:
            os.unlink(file_path)

    # def test_nonexistent_file(self):
    #     """Test that nonexistent file causes exit."""
    #     with self.assertRaises(SystemExit) as cm:
    #         send.create_attachment('/nonexistent/file.pdf')
    #     self.assertEqual(cm.exception.code, 1)


class TestParseArgs(unittest.TestCase):
    """Tests for parse_args function."""

    def test_all_arguments(self):
        """Test parsing all command-line arguments."""
        test_args = [
            'send.py',
            '--from', 'sender@example.com',
            '--to', 'recipient@example.com',
            '--subject', 'Test Subject',
            '--body', 'Test body content',
            '--files', 'file1.pdf', 'file2.epub',
            '--env', 'custom.env'
        ]
        
        with mock.patch.object(sys, 'argv', test_args):
            args = send.parse_args()
            
            self.assertEqual(args.from_email, 'sender@example.com')
            self.assertEqual(args.to_email, 'recipient@example.com')
            self.assertEqual(args.subject, 'Test Subject')
            self.assertEqual(args.body, 'Test body content')
            self.assertEqual(args.files, ['file1.pdf', 'file2.epub'])
            self.assertEqual(args.env, 'custom.env')

    def test_short_arguments(self):
        """Test parsing short-form arguments."""
        test_args = [
            'send.py',
            '-f', 'sender@example.com',
            '-t', 'recipient@example.com',
            '-s', 'Subject',
            '-b', 'Body'
        ]
        
        with mock.patch.object(sys, 'argv', test_args):
            args = send.parse_args()
            
            self.assertEqual(args.from_email, 'sender@example.com')
            self.assertEqual(args.to_email, 'recipient@example.com')
            self.assertEqual(args.subject, 'Subject')
            self.assertEqual(args.body, 'Body')

    def test_default_env_path(self):
        """Test default .env path."""
        test_args = ['send.py']
        
        with mock.patch.object(sys, 'argv', test_args):
            args = send.parse_args()
            self.assertEqual(args.env, '.env')


class TestSendEmail(unittest.TestCase):
    """Tests for send_email function."""

    def setUp(self):
        """Set up test environment."""
        os.environ['MJ_APIKEY_PUBLIC'] = 'test_public_key'
        os.environ['MJ_APIKEY_PRIVATE'] = 'test_private_key'

    def tearDown(self):
        """Clean up environment."""
        os.environ.pop('MJ_APIKEY_PUBLIC', None)
        os.environ.pop('MJ_APIKEY_PRIVATE', None)

    def test_missing_api_keys(self):
        """Test that missing API keys cause exit."""
        os.environ.pop('MJ_APIKEY_PUBLIC', None)
        
        with self.assertRaises(SystemExit) as cm:
            send.send_email(
                from_email='sender@example.com',
                to_email='recipient@example.com',
                subject='Test',
                body='Test body'
            )
        self.assertEqual(cm.exception.code, 1)

    @mock.patch('urllib.request.urlopen')
    def test_successful_send(self, mock_urlopen):
        """Test successful email send."""
        mock_response = mock.MagicMock()
        mock_response.read.return_value = b'{"Messages": [{"Status": "success"}]}'
        mock_response.__enter__ = mock.MagicMock(return_value=mock_response)
        mock_response.__exit__ = mock.MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        # Should not raise
        send.send_email(
            from_email='sender@example.com',
            to_email='recipient@example.com',
            subject='Test',
            body='Test body'
        )
        
        # Verify urlopen was called
        mock_urlopen.assert_called_once()


# Base URL for the echo server (set in TestSendEmailWithEchoServer.setUpClass)
API_URL = None


class TestSendEmailWithEchoServer(unittest.TestCase):
    """Integration tests: real HTTP server captures request; validate payload via API_URL."""

    _server = None
    _port = None

    @classmethod
    def setUpClass(cls):
        """Start echo server and set MJ_API_URL so send.py posts to it."""
        cls._server, cls._port = run_server()
        global API_URL
        API_URL = f"http://127.0.0.1:{cls._port}/"
        os.environ["MJ_API_URL"] = API_URL

    @classmethod
    def tearDownClass(cls):
        """Stop server and clear MJ_API_URL."""
        if cls._server:
            cls._server.shutdown()
        os.environ.pop("MJ_API_URL", None)
        global API_URL
        API_URL = None

    def setUp(self):
        os.environ["MJ_APIKEY_PUBLIC"] = "test_public"
        os.environ["MJ_APIKEY_PRIVATE"] = "test_private"
        clear_captured_request()

    def tearDown(self):
        os.environ.pop("MJ_APIKEY_PUBLIC", None)
        os.environ.pop("MJ_APIKEY_PRIVATE", None)

    def _get_last_request(self):
        """Fetch last captured request from echo server as dict."""
        url = f"http://127.0.0.1:{self._port}/last-request"
        with urllib.request.urlopen(url) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def test_send_email_payload_captured(self):
        """send_email POSTs correct JSON to API_URL; echo server returns it."""
        send.send_email(
            from_email="sender@example.com",
            to_email="recipient@example.com",
            subject="Test Subject",
            body="Test body content",
        )
        captured = self._get_last_request()
        self.assertEqual(captured["method"], "POST")
        body = captured["body"]
        self.assertIn("Messages", body)
        self.assertEqual(len(body["Messages"]), 1)
        msg = body["Messages"][0]
        self.assertEqual(msg["From"]["Email"], "sender@example.com")
        self.assertEqual(msg["To"][0]["Email"], "recipient@example.com")
        self.assertEqual(msg["Subject"], "Test Subject")
        self.assertEqual(msg["TextPart"], "Test body content")
        self.assertNotIn("InlinedAttachments", msg)

    def test_send_email_with_attachment_payload_captured(self):
        """send_email with files includes InlinedAttachments in payload."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as f:
            f.write("attachment content")
            path = f.name
        try:
            send.send_email(
                from_email="a@example.com",
                to_email="b@example.com",
                subject="With attachment",
                body="Body",
                files=[path],
            )
            captured = self._get_last_request()
            msg = captured["body"]["Messages"][0]
            self.assertIn("InlinedAttachments", msg)
            atts = msg["InlinedAttachments"]
            self.assertEqual(len(atts), 1)
            self.assertEqual(atts[0]["ContentType"], "text/plain")
            self.assertTrue(atts[0]["Filename"].endswith(".txt"))
            self.assertIn("Base64Content", atts[0])
        finally:
            os.unlink(path)

    def test_main_send_payload_via_api_url(self):
        """main() uses MJ_API_URL and payload is captured correctly."""
        test_args = [
            "send.py",
            "--from", "cli@example.com",
            "--to", "recipient@example.com",
            "--subject", "CLI Subject",
            "--body", "CLI body",
        ]
        with mock.patch.object(sys, "argv", test_args):
            send.main()
        captured = self._get_last_request()
        msg = captured["body"]["Messages"][0]
        self.assertEqual(msg["From"]["Email"], "cli@example.com")
        self.assertEqual(msg["To"][0]["Email"], "recipient@example.com")
        self.assertEqual(msg["Subject"], "CLI Subject")
        self.assertEqual(msg["TextPart"], "CLI body")


class TestMainIntegration(unittest.TestCase):
    """Integration tests for main function."""

    def setUp(self):
        """Set up test environment."""
        self.env_vars = {
            'MJ_APIKEY_PUBLIC': 'test_public',
            'MJ_APIKEY_PRIVATE': 'test_private',
            'MAIL_FROM': 'default@example.com',
            'MAIL_TO': 'recipient@example.com',
        }
        self.original_env = {}
        for key, value in self.env_vars.items():
            self.original_env[key] = os.environ.get(key)
            os.environ[key] = value

    def tearDown(self):
        """Restore original environment."""
        for key, original_value in self.original_env.items():
            if original_value is not None:
                os.environ[key] = original_value
            else:
                os.environ.pop(key, None)

    def test_missing_from_email(self):
        """Test that missing from_email causes error."""
        os.environ.pop('MAIL_FROM', None)
        
        test_args = ['send.py']
        with mock.patch.object(sys, 'argv', test_args):
            with self.assertRaises(SystemExit) as cm:
                send.main()
            self.assertEqual(cm.exception.code, 1)

    def test_missing_to_email(self):
        """Test that missing to_email causes error."""
        os.environ.pop('MAIL_TO', None)
        
        test_args = ['send.py', '--from', 'sender@example.com']
        with mock.patch.object(sys, 'argv', test_args):
            with self.assertRaises(SystemExit) as cm:
                send.main()
            self.assertEqual(cm.exception.code, 1)


if __name__ == '__main__':
    unittest.main()
