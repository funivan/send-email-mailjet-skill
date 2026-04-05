# Send Email via Mailjet - Claude Code Plugin

This skill enables sending emails with optional file attachments using the Mailjet API.

## Setup

Mailjet API credentials must be configured via environment variables or a `.env` file in the project root:

```bash
MJ_APIKEY_PUBLIC=your_public_key
MJ_APIKEY_PRIVATE=your_private_key
```

Optional defaults:

```bash
MAIL_FROM=sender@example.com
MAIL_TO=recipient@example.com
MAIL_SUBJECT=Hello from AI
MAIL_BODY=Default message body
MAIL_FILES_1=/path/to/attachment1.pdf
MAIL_FILES_2=/path/to/attachment2.png
```

## Usage

Use the `/send-email` command or ask Claude to send an email. The skill runs:

```bash
python3 skill/send-email-mailjet/scripts/send.py \
  --from sender@example.com \
  --to recipient@example.com \
  --subject "Subject" \
  --body "Body text" \
  --files file1.pdf file2.txt
```

All parameters are optional if configured via environment variables.

## Security

- Never commit or read `.env` files directly
- Keep total attachment size under 15MB
