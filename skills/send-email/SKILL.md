---
name: send-email
description: Send emails with attachments when users say "send email", "email this to someone", "send this file via email", or need to deliver content by email.
---

# Send Email via Mailjet

Send an email using the Mailjet API. All parameters are optional — they can be set via environment variables or a `.env` file in the project root. Extract any of the following from the user's request if provided:

- **to**: recipient email address (env: `MAIL_TO`)
- **from**: sender email address (env: `MAIL_FROM`)
- **subject**: email subject line (env: `MAIL_SUBJECT`)
- **body**: email body text (env: `MAIL_BODY`)
- **files**: file paths to attach (env: `MAIL_FILES_1`, `MAIL_FILES_2`, ...)

Only include flags for values explicitly provided by the user. Omit flags that were not mentioned — the script will use environment defaults.

## Sending the email

Run the following command with only the flags the user specified:

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
