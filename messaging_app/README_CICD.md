# CI/CD Setup for Django Messaging App

This folder contains **pipeline-as-code** for Jenkins and **GitHub Actions** to run tests, linting,
coverage reports, and to build & push Docker images.

## What’s included
- `Jenkinsfile` – Jenkins declarative pipeline
- `.github/workflows/ci.yml` – CI: tests, flake8, coverage on push/PR
- `.github/workflows/dep.yml` – CD: build & push Docker image to Docker Hub
- `Dockerfile` – Production-ready app image using Gunicorn
- `requirements.txt` – Runtime + dev/test dependencies
- `.flake8`, `pytest.ini`, `.coveragerc` – Code quality & testing config
- `scripts/entrypoint.sh` – Container startup script

## Jenkins quickstart
1. Run Jenkins (Docker):
   ```bash
   docker run -d --name jenkins -p 8080:8080 -p 50000:50000 -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts
   ```
2. Install plugins: **Git**, **Pipeline**, **ShiningPanda** (optional).
3. Add credentials:
   - `github-creds-id` (token or user/pass with repo access).
   - `dockerhub-creds-id` (Docker Hub user/pass or token).
4. Create Pipeline job using `Jenkinsfile` (SCM or inline).
5. Set parameters as needed (repo URL, branch, app dir, docker image name).
6. Run **Build Now**.

## GitHub Actions secrets
- `DOCKERHUB_USERNAME` – your Docker Hub username
- `DOCKERHUB_TOKEN` – Docker Hub access token/password

## MySQL in CI
The CI job brings up a MySQL 8 service and exposes env vars your Django settings can read:
`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`.

## Docker build locally
```bash
docker build -t yourdockerhubusername/messaging-app:dev messaging_app
docker run --rm -p 8000:8000 yourdockerhubusername/messaging-app:dev
```

## Notes
- Ensure `messaging_app.settings` reads DB params from environment variables as provided above.
- If your tests require migrations, the entrypoint performs them at container start; for CI, your tests should handle DB setup within pytest/django.
