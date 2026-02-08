# Send email via Mailjet skill

Skill for sending emails with attachments using Mailjet API.


## Installation
```
npx skills add https://github.com/funivan/send-email-mailjet-skill/ --skill send-email-mailjet
```

## Configuration

Mailjet is a reliable email delivery service with a REST API. 
This skill uses Mailjet to send transactional emails with attachments programmatically.

Go to [Mailjet](https://app.mailjet.com/dashboard) and obtain your API keys.

You can set all env variables in the system environment or create a `.env` file in the project root with the following variables:

```bash
# required for Mailjet API authentication
MJ_APIKEY_PUBLIC=your_public_key
MJ_APIKEY_PRIVATE=your_private_key
```
Now you can call the skill with parameters like sender, recipient, subject, body, and attachments.

> [!TIP]
> Send email to test@example.com from user@example.com with joke and funny subject.

You can also set default env variables for sender, recipient, subject and others:

```bash
MAIL_FROM=sender@example.com
MAIL_TO=recipient@example.com
MAIL_SUBJECT=Hello from AI
```
And specify just body in prompt:
> [!TIP]
> Send email with body "This is a test email"


### Attaching files defined in env

You can pre-configure file attachments using sequential `MAIL_FILES_N` variables:

```bash
MAIL_FILES_1=/path/to/file1.pdf
MAIL_FILES_2=/path/to/file2.epub
MAIL_FILES_3=/path/to/file3.txt
```

**Important:** Gaps in numbering stop the sequence. If `MAIL_FILES_2` is missing, only `MAIL_FILES_1` will be used.

Files will be attached in the order of their numbering in all email sends, unless overridden by command-line arguments.

## Development

### Running tests locally

From the repository root:

```bash
# Run all tests
python -m unittest discover -s tests -p "test_*.py" -v

# Run with coverage (install coverage first: pip install coverage)
coverage run --source=skill/send-email-mailjet/scripts -m unittest discover -s tests -p "test_*.py" -v
coverage report
```

Optional: create a virtual environment before installing or running:

```bash
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install coverage
# then run the coverage commands above
```
