# Security Policy

## Supported versions

Security fixes are applied to the latest published release.

## Reporting a vulnerability

Do not open a public issue or include credentials, private repository content, or personal data in a report.

Use GitHub's private vulnerability reporting form:

https://github.com/mikeqwe/system-reality-alignment-plugin/security/advisories/new

Include the affected version, reproduction steps, impact, and the smallest safe proof of concept. Reports are reviewed on a best-effort basis; remediation details will be coordinated privately before disclosure.

The installed v2 plugin contains only instructions. Developer and evaluation helpers are outside the runtime package. It does not bundle network access, MCP servers, background processes, or lifecycle hooks. Run generated candidate code only in an appropriately isolated, disposable environment.
