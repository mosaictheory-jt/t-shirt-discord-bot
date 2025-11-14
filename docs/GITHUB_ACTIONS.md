# GitHub Actions CI/CD Guide

This guide explains the GitHub Actions workflows configured for this project.

## Overview

The project uses GitHub Actions for:
- **Continuous Integration (CI)**: Automated testing and code quality checks
- **Continuous Deployment (CD)**: Automated deployment to Google Cloud Run
- **Dependency Management**: Automated dependency updates via Dependabot

## Workflows

### 1. CI/CD Pipeline (`ci.yml`)

**Trigger**: Push to `main` or `develop` branches, or pull requests

**File**: `.github/workflows/ci.yml`

#### Jobs

##### Lint Job
Checks code quality and formatting.

```yaml
- Black: Code formatting check
- Ruff: Linting and code quality
```

**Run locally**:
```bash
black --check src/ tests/
ruff check src/ tests/
```

##### Test Job
Runs the test suite on multiple Python versions.

```yaml
- Python versions: 3.11, 3.12
- Runs: pytest with coverage
- Uploads: Coverage to Codecov
```

**Run locally**:
```bash
pytest --cov=src --cov-report=term
```

##### Security Job
Scans for security vulnerabilities.

```yaml
- Bandit: Security linter for Python
- Safety: Checks for known vulnerabilities
```

**Run locally**:
```bash
bandit -r src/
safety check
```

##### Docker Job
Builds and tests the Docker image.

```yaml
- Builds: Docker image with BuildKit
- Uses: GitHub Actions cache for layers
- Tests: Python import verification
```

**Run locally**:
```bash
docker build -t discord-tshirt-bot:test .
docker run --rm discord-tshirt-bot:test python -c "import src"
```

##### Deploy Job
Deploys to Google Cloud Run (only on `main` branch).

```yaml
- Authenticates: Using GCP service account
- Builds: Container and pushes to GCR
- Deploys: To Cloud Run
- Updates: Latest tag
```

**Requirements**:
- `GCP_SA_KEY` secret (service account JSON)
- `GCP_PROJECT_ID` secret (Google Cloud project ID)
- Secrets stored in Secret Manager:
  - `discord-bot-token`
  - `google-api-key`
  - `printful-api-key`

### 2. PR Quality Check (`pr-check.yml`)

**Trigger**: Pull request opened, updated, or reopened

**File**: `.github/workflows/pr-check.yml`

#### Features

1. **Full Test Suite**: Runs all tests with coverage
2. **Coverage Check**: Fails if coverage < 70%
3. **Coverage Comment**: Posts coverage report on PR
4. **Documentation Check**: Warns if code changed without docs
5. **TODO/FIXME Check**: Lists remaining TODOs

**Manual trigger**:
```bash
# Run the same checks locally
pytest --cov=src --cov-report=term --cov-report=html
coverage report --fail-under=70
```

### 3. Dependabot (`dependabot.yml`)

**Trigger**: Weekly automatic checks

**File**: `.github/dependabot.yml`

#### Updates

- **Python dependencies**: Weekly pip checks
- **GitHub Actions**: Weekly action version checks
- **Docker base images**: Weekly Docker checks

**Configuration**:
- Creates PRs automatically
- Max 10 open PRs for Python deps
- Max 5 open PRs for Actions/Docker
- Labels PRs appropriately

## Secrets Configuration

### Required Secrets

Configure these in GitHub repository settings (Settings → Secrets and variables → Actions):

#### For Testing (Optional)
```
TEST_DISCORD_BOT_TOKEN=test_token
TEST_GOOGLE_API_KEY=test_key
TEST_PRINTFUL_API_KEY=test_key
```

These are optional - workflows will use default test values if not provided.

#### For Deployment (Required for CD)
```
GCP_SA_KEY=<service_account_json>
GCP_PROJECT_ID=<your_project_id>
```

### Setting Up Secrets

#### 1. Create Service Account

```bash
# Create service account
gcloud iam service-accounts create github-actions \
    --display-name="GitHub Actions"

# Grant necessary permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Create key
gcloud iam service-accounts keys create github-sa-key.json \
    --iam-account=github-actions@$PROJECT_ID.iam.gserviceaccount.com
```

#### 2. Add to GitHub

1. Go to repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add `GCP_SA_KEY` with the contents of `github-sa-key.json`
4. Add `GCP_PROJECT_ID` with your Google Cloud project ID

#### 3. Store Bot Credentials in Secret Manager

```bash
# Discord token
echo -n "$DISCORD_BOT_TOKEN" | gcloud secrets create discord-bot-token \
    --replication-policy="automatic" \
    --data-file=-

# Google API key
echo -n "$GOOGLE_API_KEY" | gcloud secrets create google-api-key \
    --replication-policy="automatic" \
    --data-file=-

# Printful API key
echo -n "$PRINTFUL_API_KEY" | gcloud secrets create printful-api-key \
    --replication-policy="automatic" \
    --data-file=-
```

## Workflow Triggers

### Automatic Triggers

| Event | Workflows |
|-------|-----------|
| Push to `main` | CI/CD Pipeline (with deploy) |
| Push to `develop` | CI/CD Pipeline (no deploy) |
| Pull Request | CI/CD Pipeline + PR Check |
| Weekly | Dependabot updates |

### Manual Triggers

You can manually trigger workflows from the Actions tab:

1. Go to repository → Actions
2. Select workflow
3. Click "Run workflow"
4. Choose branch
5. Click "Run workflow"

## Status Badges

Add status badges to your README:

```markdown
![CI/CD](https://github.com/username/discord-tshirt-bot/workflows/CI%2FCD%20Pipeline/badge.svg)
![Tests](https://github.com/username/discord-tshirt-bot/workflows/PR%20Quality%20Check/badge.svg)
[![codecov](https://codecov.io/gh/username/discord-tshirt-bot/branch/main/graph/badge.svg)](https://codecov.io/gh/username/discord-tshirt-bot)
```

## Debugging Workflows

### View Logs

1. Go to Actions tab
2. Click on workflow run
3. Click on job
4. Expand steps to see logs

### Common Issues

#### 1. Authentication Failures

**Problem**: `Error: google.auth.exceptions.DefaultCredentialsError`

**Solution**: Check that `GCP_SA_KEY` secret is properly set

#### 2. Permission Denied

**Problem**: Service account lacks permissions

**Solution**: Grant required roles:
```bash
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.admin"
```

#### 3. Secret Not Found

**Problem**: `Error: Secret "discord-bot-token" not found`

**Solution**: Create secrets in Secret Manager:
```bash
echo -n "$DISCORD_BOT_TOKEN" | gcloud secrets create discord-bot-token \
    --replication-policy="automatic" \
    --data-file=-
```

#### 4. Docker Build Fails

**Problem**: Docker build fails in CI

**Solution**: Test locally first:
```bash
docker build -t discord-tshirt-bot:test .
```

#### 5. Tests Fail in CI

**Problem**: Tests pass locally but fail in CI

**Solution**: 
- Check environment variables
- Ensure no hardcoded paths
- Test in clean environment:
```bash
docker run -it python:3.11-slim bash
# Inside container:
pip install pytest
# Run tests
```

### Enable Debug Logging

Add to workflow file:

```yaml
env:
  ACTIONS_STEP_DEBUG: true
  ACTIONS_RUNNER_DEBUG: true
```

## Optimizing Workflows

### Speed Improvements

1. **Caching**: Uses GitHub Actions cache for Docker layers
2. **Parallel Jobs**: Lint, test, and security run in parallel
3. **Matrix Strategy**: Tests multiple Python versions concurrently

### Cost Optimization

- **Free tier**: 2,000 minutes/month for public repos
- **Private repos**: 2,000 minutes/month with GitHub Team
- **Reduce runs**: Use path filters to skip unnecessary runs

Example:
```yaml
on:
  push:
    paths:
      - 'src/**'
      - 'tests/**'
      - 'pyproject.toml'
```

## Best Practices

### DO's

✅ **Keep secrets secret** - never log or expose them
✅ **Use matrix builds** for multiple versions
✅ **Cache dependencies** to speed up builds
✅ **Fail fast** - stop on first failure
✅ **Use artifacts** to share data between jobs
✅ **Keep workflows focused** - one workflow = one purpose

### DON'Ts

❌ **Don't hardcode secrets** in workflow files
❌ **Don't run unnecessary jobs** on every push
❌ **Don't ignore failing workflows** - fix them
❌ **Don't make workflows too complex** - keep them readable
❌ **Don't skip testing** - always run tests before deploy

## Local Development

Test GitHub Actions locally with [act](https://github.com/nektos/act):

```bash
# Install act
brew install act  # macOS
# or
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Run workflows locally
act push
act pull_request

# Run specific job
act -j test

# Use specific workflow
act -W .github/workflows/ci.yml
```

## Monitoring

### Check Workflow Status

```bash
# List recent runs
gh run list

# View specific run
gh run view <run-id>

# Watch run in progress
gh run watch
```

### Notifications

Enable notifications in GitHub settings:
- Settings → Notifications
- Check "Actions" under "Watching"
- Choose email/web notifications

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)
- [Google Cloud GitHub Actions](https://github.com/google-github-actions)

## Questions?

- Check [Actions tab](../../actions) for workflow runs
- Review [workflow files](../.github/workflows/)
- Open an issue with the `ci/cd` label
- Check GitHub Actions documentation
