# This repository provides methodology of using Gitleaks to prevent secrets (API keys, passwords, tokens) from being committed to the codebase.

# It might be enforced in two places:

- Local Git pre-commit hook (pre-commit.py)
- GitLab CI pipeline (.gitlab-ci-secrets-scan.yml)

## Local Pre-Commit Hook

### Before every commit, this hook:
- scans staged changes using Gitleaks
- blocks the commit if secrets are detected
- prints a warning message in the terminal

### Installation
1. Copy hook into Git hooks directory:
```
cp pre-commit.py .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```
2. Enable hook
```
git config hooks.gitleaks true
```

## GitLab CI Secret Scan

The CI job:
- Fetches repository code
- Installs or uses prebuilt Gitleaks
- Runs a full repository scan
- Fails the pipeline if secrets are found

### Installation
Include into gitlab pipeline
```
include:
  - project: devopsintensive/secops
    file: /templates/.gitlab-ci-secrets-scan.yml
    ref: feature/secrets-scan
...
...
secrets-test:
  extends: .secrets-scanning
  variables:
    GITLEAKS_GIT_LOGS: "HEAD~1^..HEAD"
```