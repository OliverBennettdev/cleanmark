# Security Policy

## Reporting a vulnerability

Please report security issues privately through GitHub's security reporting features when available. Do not open a public issue containing exploit details, credentials, private metadata, or sensitive file contents.

When reporting a file-processing bug, provide the smallest synthetic reproduction you can. Do not attach confidential originals.

## Security model

Cleanmark treats uploaded files as untrusted input. The default deployment keeps the cleaner service off the public host network, processes each request in an isolated temporary directory, enforces upload limits, avoids logging file contents, and deletes temporary files after processing.

No tool can guarantee that every provenance mechanism has been detected or removed. Security-sensitive workflows should validate outputs independently.
