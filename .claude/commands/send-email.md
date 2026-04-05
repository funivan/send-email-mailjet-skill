Send an email using the Mailjet API via the send-email-mailjet skill.

Gather the following from the user's request (use environment defaults from `.env` if not specified):
- **from**: sender email address (env: `MAIL_FROM`)
- **to**: recipient email address (env: `MAIL_TO`)
- **subject**: email subject (env: `MAIL_SUBJECT`, default: "Hello")
- **body**: email body text (env: `MAIL_BODY`, default: "Hello from AI")
- **files**: file paths to attach (env: `MAIL_FILES_1`, `MAIL_FILES_2`, etc.)

Build and run the command:

```bash
python3 skill/send-email-mailjet/scripts/send.py \
  --from <from> \
  --to <to> \
  --subject "<subject>" \
  --body "<body>" \
  --files <file1> <file2> ...
```

Omit any flags that were not provided and have no env default. Always confirm the recipient and subject with the user before sending. Report the API response back to the user.

Usage: $ARGUMENTS
