# Test Automation Framework

All automated test cases in this project are executed through a GitHub-based CI pipeline, enabling repeatable, version-controlled test runs in the cloud without requiring local orchestration for every execution.

A comprehensive QA automation suite for a containerized SaaS platform. This project combines black-box UI automation with API contract validation and test orchestration to provide end-to-end quality coverage for modern web applications.

## CI pipeline
**Prerequisite:** To execute the tests, create a GitHub Actions secret called `GHCR_PAT` containing a token to pull the necessary Docker images.

## Collaborate from a Codespace with a fork


1. Fork the repository on GitHub.
2. Open your fork in a GitHub Codespace.
3. Create a branch:

```bash
git checkout -b feature/my-change
```

4. Make your changes, then commit and push:

```bash
git add .
git commit -m "Add my improvement"
git push origin feature/my-change
```

5. Open a pull request from your fork on GitHub.
6. Keep your fork updated:

```bash
git fetch upstream
git rebase upstream/main
git push origin main
```



This keeps the main repo clean while letting you work and review changes in a Codespace.

## Overview

This repository demonstrates a complete automation pipeline for a SaaS product deployed in isolated Docker environments. It validates:

- API behavior using OpenAPI/Swagger-driven property-based testing
- End-to-end user flows using Selenium UI automation
- Application performance under load using JMeter load testing
- Test execution and reporting with Pytest and Allure
- Local and remote execution in GitHub Codespaces or Dockerized environments

## Tech Stack

| Technology | Category | Purpose |
| :--- | :--- | :--- |
| Pytest | Test runner | Orchestrates test execution and integration with fixtures |
| Selenium | UI automation | Automates browser interactions for E2E validation |
| Schemathesis | API testing | Generates property-based API tests from OpenAPI specs |
| Docker | Environment orchestration | Runs the app and dependencies in isolated containers |
| JMeter | Load testing | Simulates user load and measures application performance under stress |
| Allure | Reporting | Produces rich HTML reports for test outcomes |


## Test Scope

- Property-based API testing using Schemathesis against the backend Swagger/OpenAPI schema
- End-to-end UI validation for user journeys and critical flows
- Load testing with JMeter to measure application performance and identify bottlenecks
- CI-friendly execution with headless browser support and report generation
- Visual debugging support using VNC for local and remote development workflows

## Prerequisites

Before starting, ensure the following tools are installed:

- Docker and Docker Compose
- Python 3.x
- Node.js and npm
- Git

## Environment Setup

Create a `.env` file in the project root with the following values(local setup)

If you open this repository in a browser-accessible for example Codespace, the frontend and backend will be served under a proxy HTTPS hostname rather than `localhost`. 

Url example:  
Local: http://127.0.0.1:8000  
Codespace: https://<hash>-8000.app.github.dev
:

```env
# Frontend
REACT_APP_API_HOST=http://127.0.0.1:8000
REACT_APP_FRONTEND_HOST=http://127.0.0.1:3000

# Backend
BACKEND_HOST=http://127.0.0.1:8000
FRONTEND_HOST=http://127.0.0.1:3000
ALLOWED_HOSTS=localhost,127.0.0.1, ,https://<hash>-8000.app.github.dev,https://<hash>-3000.app.github.dev

SECRET_KEY=your_secret_key
# Django admin
DJANGO_ADMIN_USER=your_admin
DJANGO_ADMIN_EMAIL=your_admin@local.local
DJANGO_ADMIN_PASSWORD=your_password

# Tests
TEST_API_BASE_URL=http://127.0.0.1:8000
TEST_API_ADMIN_USERNAME=your_admin
TEST_API_ADMIN_PASSWORD=your_password
MAILPIT_HOST=http://127.0.0.1:8025
TEST_UI_BASE_URL=http://127.0.0.1:3000
UI_BROWSER=chrome
# UI Test headless = false / install browser local or use VNC over Codespace
UI_HEADLESS=true
MOBILE=false
```

### Optional CLI overrides

The values above are the default environment settings used by the suite, but they can be overridden at runtime with pytest CLI options. CLI flags take precedence over the matching environment variables.

| Environment variable | Pytest CLI option |
| :--- | :--- |
| `TEST_API_BASE_URL` | `--api-base-url` |
| `TEST_API_ADMIN_USERNAME` | `--api-admin-username` |
| `TEST_API_ADMIN_PASSWORD` | `--api-admin-password` |
| `UI_BROWSER` | `--ui-browser` |
| `UI_HEADLESS` | `--ui-headless` |
| `TEST_UI_BASE_URL` | `--ui-base-url` |
| `MAILPIT_HOST` | `--api-mailpit-host` |
| `MOBILE` | `--mobile` |

Example:

```bash
pytest -m "api or ui" \
  --api-base-url=http://127.0.0.1:8000 \
  --api-admin-username=admin \
  --api-admin-password=secret \
  --ui-browser=chrome \
  --ui-headless=true \
  --ui-base-url=http://127.0.0.1:3000
```

This is useful when you want to run the same suite against a different environment without changing the project `.env` file.

## Getting Started

### 1) Start the target application

Pull the Docker images and start the app stack:

```bash
export GITHUB_TOKEN="token_here"
echo "$GITHUB_TOKEN" | docker login ghcr.io -u github_username --password-stdin
docker compose -f docker-compose-pull.yml pull
docker compose -f docker-compose-pull.yml up -d
```

### 2) Set up a Python virtual environment

```bash
python3 -m venv tests/venv
source tests/venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
or use: __./scripts/setup_python_virtual_environment.sh__

### 3) Install browser(Chrome) dependencies

For Linux-based UI testing, install Chromium and Google Chrome:

```bash
sudo apt-get update
sudo apt-get install -y chromium chromium-driver
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt-get install -y ./google-chrome-stable_current_amd64.deb
google-chrome --version
```
or use: __./scripts/install_chrome_dependencies.sh__

### 4) Configure JMeter in Linux/Codespace

Install JMeter:
```bash
wget https://downloads.apache.org/jmeter/binaries/apache-jmeter-5.6.3.tgz
tar -xzf apache-jmeter-5.6.3.tgz
```
or use: __./scripts/install_jmeter.sh__

Then use the Linux binary path:
```bash
export JMETER_HOME=/workspaces/test-automation-framework/apache-jmeter-5.6.3
export PATH="$JMETER_HOME/bin:$PATH"
which jmeter
```
or use: __./scripts/export_jmeter.sh__




## Running Tests

Make sure your virtual environment is active before running the suite.

### Run all tests

```bash
pytest -m "contract or api or ui"
```

### Run API tests only

```bash
pytest -m "api"
```

### Run UI tests only

```bash
pytest -m "ui"
```

## Test Reporting with Allure

Test results are stored in `tests/allure-results`.

Install Allure CLI:

```bash
npm install -g allure-commandline
```
or use: __./scripts/install_allure.sh__

View the report locally:

```bash
allure serve tests/allure-results
```
or use: __./scripts/view_allure_results_local.sh__

Generate a static report on a remote or Codespace environment:

```bash
allure generate tests/allure-results -o allure-report --clean
python3 -m http.server 8001 --directory allure-report
```
or use: __./scripts/view_allure_results_remote.sh__

Then open the forwarded port `8001` in your browser.

## Test Reporting JMeter

```bash
python3 -m http.server 8001 --directory ./tests/performance/report
```
or use: __./scripts/report_jmeter.sh__



## Visual Debugging with VNC

When working in GitHub Codespaces or remote environments, you can run UI tests with a visible browser window by exposing a virtual desktop.

For development / debugging with Codespace install extensions:  "Python Debugger", "Python", "Pylance" on your codespace

### 1) Install VNC dependencies

```bash
sudo apt-get install -y xvfb x11vnc fluxbox novnc
```
or use: __./scripts/install_vnc.sh__

### 2) Start the virtual desktop

```bash
Xvfb :99 -screen 0 1920x1080x24 &

export DISPLAY=:99

fluxbox >/tmp/fluxbox.log 2>&1 &

x11vnc -display :99 -forever -shared -rfbport 5900 -nopw >/tmp/x11vnc.log 2>&1 & /usr/share/novnc/utils/novnc_proxy --vnc localhost:5900 --listen 6080 >/tmp/novnc.log 2>&1 &
```
or use: __./scripts/start_vnc_desktop.sh__

### 3) Connect to the browser session

Open:

```text
http://localhost:6080/vnc.html
```

Then click Connect.

### 4) Run UI tests visually

```bash
export DISPLAY=:99
export CHROME_BINARY=/usr/bin/google-chrome

pytest tests/ui -m ui --ui-headless false
```

or use: __./scripts/run_ui_tests_no_headless.sh__

You can also set `UI_HEADLESS=false` and `DISPLAY=:99` in your `.env` file for use with the VS Code testing panel.

### 5) Open Jmeter GUI with VNC
```bash
export DISPLAY=:99
export JMETER_HOME=/workspaces/test-automation-framework/apache-jmeter-5.6.3
export PATH="$JMETER_HOME/bin:$PATH"
jmeter
```
or use: __./scripts/start_jmeter_in_vnc.sh__

## VS Code Configuration Tips

1. Select the correct Python interpreter:
   - Press `Ctrl+Shift+P`
   - Run `Python: Select Interpreter`
   - Choose `./tests/venv/bin/python`

2. Disable preview tab behavior for files:
   - Press `Ctrl+Shift+P`
   - Open `Preferences: Open User Settings (JSON)`
   - Add:

```json
{
  "workbench.editor.enablePreview": false,
  "workbench.editor.enablePreviewFromQuickOpen": false
}
```


## License

This project is licensed under the MIT License.
