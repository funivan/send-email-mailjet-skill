# Changelog

## [Unreleased]

### Added
- Claude Code plugin support via `.claude-plugin/` manifests and `skills/send-email/SKILL.md`.
- Marketplace configuration for one-command installation in Claude Code.

### Changed
- **Breaking:** Environment variables renamed from `MAIL_*` to `MJ_*` prefix for consistency:
  - `MAIL_FROM` → `MJ_FROM`
  - `MAIL_TO` → `MJ_TO`
  - `MAIL_SUBJECT` → `MJ_SUBJECT`
  - `MAIL_BODY` → `MJ_BODY`
  - `MAIL_FILES_N` → `MJ_FILES_N`
- The old `MAIL_*` names still work as a deprecated fallback with a warning printed to stderr.

### Migration
If you have an existing `.env` file, rename your variables from `MAIL_*` to `MJ_*`. The old names will continue to work but will emit deprecation warnings.
