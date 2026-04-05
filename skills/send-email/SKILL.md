---
name: send-email
description: Send emails with attachments when users say "send email", "email this to someone", "send this file via email", or need to deliver content by email.
---

# Send Email via Mailjet

Send an email using the Mailjet API. Extract the following from the user's request:

- **to**: recipient email address
- **from**: sender email address (optional if configured)
- **subject**: email subject line
- **body**: email body text
- **files**: file paths to attach (optional, space-separated)

## Sending the email

Run the following command, omitting any flags that were not provided:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skill/send-email-mailjet/scripts/send.py \
  --from "sender@example.com" \
  --to "recipient@example.com" \
  --subject "Subject line" \
  --body "Email body text" \
  --files path/to/file1.pdf path/to/file2.txt
```

## Environment variables

The script reads these from the environment or a `.env` file:

- `MJ_APIKEY_PUBLIC` / `MJ_APIKEY_PRIVATE` — Mailjet API credentials (required)
- `MAIL_FROM` — default sender email
- `MAIL_TO` — default recipient email
- `MAIL_SUBJECT` — default subject (fallback: "Hello")
- `MAIL_BODY` — default body (fallback: "Hello from AI")
- `MAIL_FILES_1`, `MAIL_FILES_2`, ... — default file attachments

## Important

- Always confirm the recipient and subject with the user before sending
- Keep total attachment size under 15MB
- Never read or expose `.env` files directly

Report the API response back to the user after sending.
