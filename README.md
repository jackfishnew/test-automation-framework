# Test Automation Framework

A comprehensive QA automation suite for a containerized SaaS platform. This project combines black-box UI automation with API contract validation and test orchestration to provide end-to-end quality coverage for modern web applications.

All automated test cases in this project are executed through a GitHub-based CI pipeline, enabling repeatable, version-controlled test runs in the cloud without requiring local orchestration for every execution.

## Overview

This repository demonstrates a complete automation pipeline for a SaaS product deployed in isolated Docker environments. It validates:

- Contract and REST API validation using OpenAPI/Swagger-driven testing
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
| Taurus | Orchestration | Coordinates and executes JMeter test plans with configurable load profiles and reusable test configuration |
| JMeter | Load testing | Generates realistic user traffic and measures application performance under load |
| Allure | Reporting | Produces rich HTML reports for test outcomes |


## Test Scope

- Property-based API testing using Schemathesis against the backend Swagger/OpenAPI schema
- End-to-end UI validation for user journeys and critical flows
- Load testing with JMeter to measure application performance and identify bottlenecks
- CI-friendly execution with headless browser support and report generation
- Visual debugging support using VNC for local and remote development workflows



## Environment Setup for GitHub Actions CI

The CI pipeline reads configuration from GitHub Actions secrets and variables. Values are injected into the test environment and Docker Compose configuration before the application stack and test suites are started.

Required GitHub Actions configuration:
- `GHCR_PAT` — GitHub Container Registry token used to pull the required Docker images.

Recommended GitHub secrets:
- `SECRET_KEY`
- `DJANGO_ADMIN_USER`
- `DJANGO_ADMIN_EMAIL`
- `DJANGO_ADMIN_PASSWORD`

Recommended GitHub variables:
- `BACKEND_HOST`
- `FRONTEND_HOST`
- `ALLOWED_HOSTS`
- `REACT_APP_FRONTEND_HOST`
- `TEST_API_BASE_URL`
- `TEST_UI_BASE_URL`
- `MAILPIT_HOST`
- `UI_BROWSER`
- `UI_HEADLESS`
- `VUSERS`
- `RAMPUP`
- `HOLDFOR`

If a secret or variable is not defined, the workflow falls back to local development defaults such as `http://localhost:8000` and `http://localhost:3000`.

Example GitHub configuration:

```bash
# GitHub Secrets
GHCR_PAT=your_github_token
SECRET_KEY=your_secret_key
DJANGO_ADMIN_USER=your_admin
DJANGO_ADMIN_EMAIL=your_admin@local.local
DJANGO_ADMIN_PASSWORD=your_password

# GitHub Variables
BACKEND_HOST=http://localhost:8000
FRONTEND_HOST=http://localhost:3000
ALLOWED_HOSTS=localhost,127.0.0.1
REACT_APP_FRONTEND_HOST=http://localhost:3000
TEST_API_BASE_URL=http://localhost:8000/
TEST_UI_BASE_URL=http://localhost:3000/
MAILPIT_HOST=http://localhost:8025
UI_BROWSER=chrome
UI_HEADLESS=true
VUSERS=2
RAMPUP=3s
HOLDFOR=20s
```

The workflow creates a `.env` file automatically at runtime from these values, which is then used by Docker Compose and the test suite.

To start the CI workflow, push a commit to a branch or open a pull request in the repository. GitHub Actions will automatically trigger the pipeline and execute the contract, API, UI, and load tests in sequence.

## Environment Setup

This setup was tested locally on Ubuntu and GitHub Codespaces.

Before starting, ensure the following tools are installed:

- Docker and Docker Compose
- Python 3.x
- Node.js and npm
- Git
- Java JDK

Use: ./scripts/setup_basic.sh

Normally, when you add your user account to the docker group (using sudo usermod -aG docker $USER), you need to log out and log back in (or reboot) for the system to recognize your new permissions

Create a `.env` file in the project root with the values required for local execution.

When working in a browser-accessible environment such as GitHub Codespaces, the application is typically exposed through a proxy HTTPS endpoint rather than `localhost`. In those cases, use the generated Codespace URL instead of the local host address.

Example URLs:
- Local: `http://127.0.0.1:8000`
- Codespace: `https://<hash>-8000.app.github.dev`

```env
# Target application
REACT_APP_API_HOST=http://127.0.0.1:8000
REACT_APP_FRONTEND_HOST=http://127.0.0.1:3000
BACKEND_HOST=http://127.0.0.1:8000
FRONTEND_HOST=http://127.0.0.1:3000
ALLOWED_HOSTS=localhost,127.0.0.1, ,https://<hash>-8000.app.github.dev,https://<hash>-3000.app.github.dev
SECRET_KEY=your_secret_key
DJANGO_ADMIN_USER=your_admin
DJANGO_ADMIN_EMAIL=your_admin@local.local
DJANGO_ADMIN_PASSWORD=your_password

# Functional tests
TEST_API_BASE_URL=http://127.0.0.1:8000
TEST_API_ADMIN_USERNAME=your_admin
TEST_API_ADMIN_PASSWORD=your_password
MAILPIT_HOST=http://127.0.0.1:8025
TEST_UI_BASE_URL=http://127.0.0.1:3000
UI_BROWSER=chrome
# UI Test headless = false / install browser locally or use VNC in Codespaces
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
The application designated for testing is a web-based Software as a Service (SaaS) solution for small sports club management ahead of its upcoming public release.

Pull the required Docker images and start the target application stack:

```bash
export GITHUB_TOKEN="token_here"
echo "$GITHUB_TOKEN" | docker login ghcr.io -u github_username --password-stdin
docker compose -f docker-compose-pull.yml pull
docker compose -f docker-compose-pull.yml up -d
```

### 2) Set up a Python virtual environment and test depedencies

```bash
sudo apt install python3.14-venv
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




## Running Functional Testing

Make sure your virtual environment is active before running the suite.

### Run all tests

```bash
pytest -m "contract or api or ui"
```

### Run API Contract tests only

```bash
pytest -m "contract"
```

### Run API tests only

```bash
pytest -m "api"
```

### Run UI tests only

```bash
pytest -m "ui"
```

### Test Reporting with Allure

Test results are stored in `tests/allure-report`.

Install Allure CLI:

```bash
sudo npm install -g allure-commandline
```
or use: __./scripts/install_allure.sh__

View the report locally:

```bash
allure serve tests/allure-report
```
or use: __./scripts/view_allure_results_local.sh__

Generate a static report on a remote or Codespace environment:

```bash
allure generate tests/allure-report -o allure-report --clean
python3 -m http.server 8001 --directory allure-report
```
or use: __./scripts/view_allure_results_remote.sh__

Then open the forwarded port `8001` in your browser.
## Running Non-Functional Testing

The load test configuration requires the following parameters to be defined:

- `concurrency`: number of concurrent virtual users
- `ramp-up`: duration required to reach the target concurrency level
- `hold-for`: duration for which the target load is sustained

```bash
pytest tests/performance/technical/test_technical_update_jmeter_target.py

python -m bzt \
  -o settings.artifacts-dir="tests/jmeter-report" \
  -o execution.1.concurrency="4" \
  -o execution.1.ramp-up="10s" \
  -o execution.1.hold-for="40s" \
  tests/performance/taurus_test_suite.yml
```

## Test Reporting JMeter

```bash
apache-jmeter-5.6.3/bin/jmeter -g "tests/jmeter-report/kpi.jtl" -o tests/jmeter-report/html

python3 -m http.server 8001 --directory ./tests/jmeter-report
```
or use: __./scripts/report_jmeter.sh__

then open  http://localhost:8001/html/index.html


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
