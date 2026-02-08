# Send email via Mailjet skill

Skill for sending emails with attachments using Mailjet API.

## Configuration
Go to [Mailjet](https://app.mailjet.com/dashboard) and obtain your API keys. Create a `.env` file in the project root with the following variables:

```bash
MJ_APIKEY_PUBLIC=your_public_key
MJ_APIKEY_PRIVATE=your_private_key
```
Specify them in .env file (or global environment)
Now you can call the skill with parameters like sender, recipient, subject, body, and attachments.

> Send email to test@example.com from user@example.com with funny subject body and some strange subject

You can also set default values in the `.env` file:

```bash
MAIL_FROM=sender@example.com
MAIL_TO=recipient@example.com
MAIL_SUBJECT=Hello from AI
```
And specify just body in prompt:

> Send email with body "This is a test email"

### Sending Attachments
To send files, provide file paths as arguments
> Send email

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
