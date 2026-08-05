# Security Policy

## Scope

This security policy covers:

- Vulnerabilities in platform code (validation scripts, MCP server, any tooling)
- Issues in GitHub Actions workflows that could allow untrusted code execution
- Exposure of private source information through repository misconfiguration
- Any mechanism by which a malicious contribution could compromise the integrity of the evidence model

It does not cover:

- Disagreements with findings (use the claim challenge process in [PEER_REVIEW.md](PEER_REVIEW.md))
- Platform content (use the bug report issue template)

## Supported Versions

| Version | Security Support |
|---|---|
| 0.x (pre-alpha) | Best effort — no formal support commitment exists before 1.0 |

There are no tagged releases yet. Security-relevant fixes land on `main`.

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Report security vulnerabilities via [GitHub private vulnerability reporting](https://github.com/egarcia74/body-of-evidence/security/advisories/new) (Security tab → Report a vulnerability). This repository has private vulnerability reporting enabled — the report is visible only to the maintainer until a fix is ready.

Include:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if you have one)

## Response Timeline

- **Acknowledgement:** Within 72 hours
- **Initial assessment:** Within 7 days
- **Fix or mitigation:** Dependent on severity; critical issues prioritised
- **Disclosure:** Coordinated with the reporter after fix is deployed

## Source Confidentiality

If a security issue involves the potential exposure of a confidential source (a person who provided information with an expectation of anonymity), this is treated as the highest severity. Response will be immediate.

## Safe Harbour

We will not pursue legal action against security researchers who report vulnerabilities in good faith, follow responsible disclosure practices, and do not access, modify, or disclose user data beyond what is necessary to demonstrate the vulnerability.
