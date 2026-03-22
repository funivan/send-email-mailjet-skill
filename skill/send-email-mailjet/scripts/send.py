#!/usr/bin/env python3
import os
import sys
import json
import base64
import argparse
import mimetypes
import urllib.request
import urllib.parse
import urllib.error
from typing import List, Optional


# Register additional MIME types not in the standard library
mimetypes.add_type('text/markdown', '.md')
mimetypes.add_type('application/epub', '.epub')
mimetypes.add_type('application/x-fictionbook+xml', '.fb2')


def load_env_file(env_path: str = '.env') -> None:
    """Load environment variables from a .env file."""
    if not os.path.exists(env_path):
        return
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, _, value = line.partition('=')
                key = key.strip()
                value = value.strip()
                # Strip surrounding single or double quotes if present, then set env var
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                # Do not overwrite existing environment variables; let existing
                # variables take precedence over values from the file.
                if key not in os.environ:
                    os.environ[key] = value


def get_files_from_env() -> List[str]:
    """Get file paths from MAIL_FILES_1, MAIL_FILES_2, etc. environment variables."""
    files = []
    i = 1
    while True:
        key = f'MAIL_FILES_{i}'
        value = os.environ.get(key)
        if value is None:
            break
        files.append(value)
        i += 1
    return files


def get_content_type(file_path: str) -> str:
    """Get content type using Python's built-in mimetypes module."""
    content_type, _ = mimetypes.guess_type(file_path)
    if content_type is None:
        content_type = 'application/octet-stream'
    return content_type


def create_attachment(file_path: str) -> dict:
    """Create an attachment dict from a file path."""
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist", file=sys.stderr)
        sys.exit(1)

    original_name = os.path.basename(file_path)
    # Sanitize filename by replacing spaces and tabs with underscores
    sanitized_name = original_name.replace(' ', '_').replace('\t', '_')
    content_type = get_content_type(file_path)
    with open(file_path, 'rb') as f:
        file_content = f.read()
    base64_content = base64.b64encode(file_content).decode('ascii')

    attachment = {
        "ContentType": content_type,
        "Filename": sanitized_name,
        "ContentID": sanitized_name,
        "Base64Content": base64_content
    }

    return attachment


def send_email(
    from_email: str,
    to_email: str,
    subject: str,
    body: str,
    files: Optional[List[str]] = None
) -> None:
    """Send an email with optional attachments using Mailjet API."""
    # Get API keys from environment variables
    mj_apikey_public = os.environ.get('MJ_APIKEY_PUBLIC')
    mj_apikey_private = os.environ.get('MJ_APIKEY_PRIVATE')

    if not mj_apikey_public or not mj_apikey_private:
        print("Error: MJ_APIKEY_PUBLIC and MJ_APIKEY_PRIVATE environment variables must be set")
        sys.exit(1)

    # Build message payload
    message: dict = {
        "From": {"Email": from_email},
        "To": [{"Email": to_email}],
        "Subject": subject,
        "TextPart": body,
    }

    # Add attachments if provided
    if files:
        attachments = []
        for file_path in files:
            attachment = create_attachment(file_path)
            attachments.append(attachment)
        message["InlinedAttachments"] = attachments

    json_payload = {"Messages": [message]}


    # Make HTTP request
    # Allow overriding the Mailjet API URL via MJ_API_URL env var (keeps default for compatibility)
    url = os.environ.get('MJ_API_URL', 'https://api.mailjet.com/v3.1/send')
    json_data = json.dumps(json_payload, ensure_ascii=False).encode('utf-8')

    # Create basic auth header
    credentials = f"{mj_apikey_public}:{mj_apikey_private}"
    auth_string = base64.b64encode(credentials.encode('utf-8')).decode('ascii')

    request = urllib.request.Request(url, data=json_data)
    request.add_header('Content-Type', 'application/json')
    request.add_header('Authorization', f'Basic {auth_string}')

    try:
        with urllib.request.urlopen(request) as response:
            response_data = response.read().decode('utf-8')
            print(response_data)
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}", file=sys.stderr)
        error_body = e.read().decode('utf-8')
        print(error_body, file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Send email with optional attachments via Mailjet API.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Environment variables (can be set in .env file):
  MJ_APIKEY_PUBLIC   Mailjet public API key (required)
  MJ_APIKEY_PRIVATE  Mailjet private API key (required)
  MJ_API_URL         Mailjet API URL (optional, default: https://api.mailjet.com/v3.1/send)
  MAIL_FROM          Default sender email
  MAIL_TO            Default recipient email
  MAIL_SUBJECT       Default email subject (default: Hello)
  MAIL_BODY          Default email body (default: Hello from AI)
  MAIL_FILES_1       First file attachment
  MAIL_FILES_2       Second file attachment (and so on...)

Examples:
  %(prog)s --from sender@example.com --to recipient@example.com --subject "Hello" --body "Message"
  %(prog)s --files document.pdf image.png
  %(prog)s  # Uses defaults from .env file
        '''
    )

    parser.add_argument(
        '--from', '-f',
        dest='from_email',
        type=str,
        help='Sender email address'
    )
    parser.add_argument(
        '--to', '-t',
        dest='to_email',
        type=str,
        help='Recipient email address'
    )
    parser.add_argument(
        '--subject', '-s',
        type=str,
        help='Email subject'
    )
    parser.add_argument(
        '--body', '-b',
        type=str,
        help='Email body text'
    )
    parser.add_argument(
        '--files',
        type=str,
        nargs='*',
        help='File paths to attach'
    )
    parser.add_argument(
        '--env',
        type=str,
        default='.env',
        help='Path to .env file (default: .env)'
    )

    return parser.parse_args()


def main() -> None:
    """Main entry point."""
    args = parse_args()

    # Load environment variables from .env file
    load_env_file(args.env)

    # Get values from args or environment variables
    from_email: str = args.from_email or os.environ.get('MAIL_FROM', '')
    to_email: str = args.to_email or os.environ.get('MAIL_TO', '')
    subject: str = args.subject or os.environ.get('MAIL_SUBJECT', 'Hello')
    body: str = args.body or os.environ.get('MAIL_BODY', 'Hello from AI')

    # Get files from args or environment variables
    files: List[str] = []
    if args.files:
        files = args.files
    else:
        files = get_files_from_env()

    # Validate required fields
    if not from_email:
        print("Error: --from is required (or set MAIL_FROM in environment)", file=sys.stderr)
        sys.exit(1)
    if not to_email:
        print("Error: --to is required (or set MAIL_TO in environment)", file=sys.stderr)
        sys.exit(1)

    # Send the email
    send_email(from_email, to_email, subject, body, files if files else None)


if __name__ == '__main__':
    main()
