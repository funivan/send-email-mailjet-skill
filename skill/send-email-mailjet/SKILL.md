---
name: send-email-mailjet
description: Send emails with attachments via Mailjet API.
compatibility:
  - python3
---

# Send Email (Mailjet)

Send emails with optional file attachments using the Mailjet API.

## When to Use

- Sending files by email (PDFs, EPUBs, documents)
- Sending ebooks to Kindle email addresses
- Emailing generated content to recipients
- Triggered by: "send email", "email file", "надіслати email", "відправити листа"

## Setup

Before using this skill, configure email settings:

1. **Get Mailjet API credentials** from [Mailjet](https://www.mailjet.com/)

2. **Create a `.env` file** in the project root with your credentials:

```bash
# Required - Mailjet API keys
MJ_APIKEY_PUBLIC=your_public_key
MJ_APIKEY_PRIVATE=your_private_key

# Optional defaults
MAIL_FROM=sender@example.com
MAIL_TO=recipient@example.com
MAIL_SUBJECT=Email subject
MAIL_BODY=Email body text

# Optional file attachments (sequential numbering)
MAIL_FILES_1=/path/to/file1.pdf
MAIL_FILES_2=/path/to/file2.epub
```

See [assets/.env.example](assets/.env.example) for a complete template.

## Instructions

Run the email script with command-line arguments:

```bash
python scripts/send.py \
  --from sender@example.com \
  --to recipient@example.com \
  --subject "Hello" \
  --body "Message body" \
  --files document.pdf image.png
```

### Arguments

| Argument | Short | Description |
|----------|-------|-------------|
| `--from` | `-f` | Sender email address |
| `--to` | `-t` | Recipient email address |
| `--subject` | `-s` | Email subject |
| `--body` | `-b` | Email body text |
| `--files` | | File paths to attach (space-separated) |
| `--env` | | Path to .env file (default: `.env`) |

### Using .env defaults

If you configure defaults in `.env`, you can run with minimal arguments:

```bash
# Send with all defaults from .env
python scripts/send.py

# Override just the recipient
python scripts/send.py --to different@example.com
```

### File attachments from .env

Use sequential `MAIL_FILES_N` variables:

```bash
MAIL_FILES_1=/path/to/file1.pdf
MAIL_FILES_2=/path/to/file2.epub
MAIL_FILES_3=/path/to/file3.txt
```

Gaps in numbering stop the sequence (e.g., if `MAIL_FILES_2` is missing, only `MAIL_FILES_1` is used).

## Supported File Types

File types are automatically detected using Python's built-in `mimetypes` module. Common types include:
Unknown file types default to `application/octet-stream`.

## Examples

**Send a PDF file:**

```bash
python scripts/send.py \
  -f sender@gmail.com \
  -t reader@kindle.com \
  -s "Book" \
  --files book.epub
```

**Send multiple files:**

```bash
python scripts/send.py \
  -f sender@gmail.com \
  -t recipient@example.com \
  -s "Documents" \
  -b "Please find attached documents." \
  --files report.pdf notes.md data.txt
```

