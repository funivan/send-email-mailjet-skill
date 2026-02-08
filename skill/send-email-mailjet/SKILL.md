---
name: send-email-mailjet
description: Helps users send emails with attachments when they say "send this file via email", "email this to someone", "send email", or need to deliver generated content by email.
compatibility:
  - python3
---

# Send Email (Mailjet)

This skill enables you to send emails with optional file attachments using the Mailjet API. Perfect for sharing documents, automating notifications, and delivering generated content.

## When to Use This Skill

Use this skill when the user:

- Says "send this file via email" or "email this document to someone"
- Requests "send file @path/to/file.md to test@example.com"
- Asks "can you email this to someone"
- Needs to deliver generated content (PDFs, EPUBs, reports) by email
- Wants to share multiple files with a recipient
- Needs to automate email delivery as part of a workflow

## Quick Start

### Prerequisites

1. Set up Mailjet API credentials in your system env or in `.env` file:
```bash
MJ_APIKEY_PUBLIC=your_public_key
MJ_APIKEY_PRIVATE=your_private_key
```

2. Optionally configure default values:
```bash
MAIL_FROM=sender@example.com
MAIL_TO=default-recipient@example.com
MAIL_SUBJECT=Default Subject
MAIL_BODY=Default message body
# Attachments: MAIL_FILES_1, MAIL_FILES_2, ...
MAIL_FILES_1=path/to/attachment1.pdf
MAIL_FILES_2=path/to/attachment2.png
```

### Usage with all parameters

```bash
python3 scripts/send.py \
  --from sender@example.com \
  --to recipient@example.com \
  --subject "Hello" \
  --body "Message body" \
  --files document.pdf image.png
```

## Command-Line Arguments

| Argument    | Short | Description                                   | Required |
| ----------- | ----- | --------------------------------------------- | -------- |
| `--from`    | `-f`  | Sender email address                          | No\*     |
| `--to`      | `-t`  | Recipient email address                       | No\*     |
| `--subject` | `-s`  | Email subject                                 | No\*     |
| `--body`    | `-b`  | Email body text                               | No\*     |
| `--files`   |       | File paths to attach (space-separated)        | No       |
| `--env`     |       | Path to custom .env file (default: `.env`)    | No       |

\*Required unless set in environment variables or .env file

## Usage Examples

### Example 1: Send Email with Full Parameters

Send a complete email with all fields specified:

```bash
python3 scripts/send.py \
  --from sender@company.com \
  --to recipient@example.com \
  --subject "Project Update" \
  --body "Hi there, here's the latest update on our project."
```

### Example 2: Send Email with Body and Subject Only

Using defaults from environment variable for sender and recipient:

```bash
python3 scripts/send.py --subject "Weekly Report" --body "Please find this week's summary attached."
```

### Example 3: Send Email with To and Subject

Override recipient and subject while using default body:

```bash
python3 scripts/send.py --to colleague@example.com --subject "Meeting Notes"
```

### Example 4: Send File to Specific Recipient

Send a single file to a recipient:

```bash
python3 scripts/send.py --to test@example.com --subject "Document for Review" --files path/to/file.md
```

**Natural language equivalent:** "send file @path/to/file.md to test@example.com"

### Example 5: Send Multiple Files with Custom Message

Share several documents in one email:

```bash
python3 scripts/send.py \
  --from sender@gmail.com \
  --to recipient@example.com \
  --subject "Project Documents" \
  --body "Please find attached all project documentation." \
  --files report.pdf notes.md presentation.pptx
```

### Example 6: Send with Minimal Arguments

Using comprehensive environment variable defaults, only override the recipient:

```bash
python3 scripts/send.py --to different@example.com
```

### Example 7: Send Generated Report

After generating a PDF report, send it to a client:

```bash
python3 scripts/send.py \
  --to client@company.com \
  --subject "Your Monthly Report is Ready" \
  --body "Thank you for your patience. Please find your generated report attached." \
  --files generated_report.pdf
```

### Example 7: Send Data Files to Team

Share data analysis results with your team:

```bash
python3 scripts/send.py \
  --from analyst@company.com \
  --to team@company.com \
  --subject "Q4 Data Analysis Results" \
  --body "Here are the results from our Q4 data analysis. Please review the CSV and JSON files." \
  --files results.csv metadata.json summary.txt
```

### Example 9: Send with Custom .env File

Use a different environment configuration file:

```bash
python3 scripts/send.py \
  --env .env.production \
  --to user@example.com \
  --subject "Production Notification" \
  --body "This email was sent using production credentials."
```

## Best Practices

### Email Composition

1. **Clear Subjects:** Use descriptive subjects that help recipients identify the purpose
2. **Professional Body Text:** Include context and call-to-action in the email body
3. **File Size Limits:** Keep total attachment size under 15MB (Mailjet's typical limit)
4. **File Naming:** Use clear, descriptive filenames for attachments

### Security & Privacy

1. **Protect API Keys:** Never commit or read directly `.env` files
2. **Data Sensitivity:** Be mindful of sensitive information in attachments

