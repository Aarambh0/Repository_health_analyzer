# Repository Health Analyzer

A Python-based tool that analyzes public GitHub repositories and generates a preliminary health report using repository structure, dependency manifests, CI/CD configuration, and recent commit activity.

## Overview

The Repository Health Analyzer helps developers quickly understand the basic engineering practices visible in a public GitHub repository. It combines a FastAPI backend with a Streamlit dashboard to present repository metadata, structural checks, dependency file detection, workflow configuration, and recent commit activity.

**Important:** The health score is a preliminary structural assessment. It is not a complete code-quality, security, or vulnerability audit.

## Features

* **GitHub Repository Analysis:** Retrieves repository metadata, including stars, forks, open issues, primary language, and default branch.
* **Repository Structure Analysis:** Checks for README documentation, a tests directory, dependency manifests, `.gitignore`, and GitHub Actions workflows.
* **Dependency Manifest Detection:** Identifies supported dependency and lockfiles, including Python, Node.js, Java, Rust, and Go manifests.
* **CI/CD Configuration Analysis:** Detects workflow files in `.github/workflows/`.
* **Repository Activity Analysis:** Examines up to 100 recent commits and estimates activity over a configurable time window.
* **Health Scoring:** Calculates a score out of 100 using five weighted structural checks.
* **Recommendations:** Identifies missing structural practices and suggests improvements.
* **Automated Testing:** Uses pytest to verify analysis logic and API behavior.

## Technology Stack

| Component             | Technology      |
| --------------------- | --------------- |
| Programming language  | Python          |
| Backend API           | FastAPI         |
| Interactive dashboard | Streamlit       |
| GitHub integration    | GitHub REST API |
| HTTP client           | Requests        |
| Automated testing     | pytest          |
| API testing support   | HTTPX           |

## Architecture

```text
User
 |
 v
Streamlit Dashboard
 |
 v
FastAPI Backend
 |
 v
Repository Analysis Endpoint
 |
 +--> GitHub Repository Metadata
 |
 +--> Repository Structure Analysis
 |
 +--> Dependency Manifest Analysis
 |
 +--> CI/CD Workflow Detection
 |
 +--> Commit Activity Analysis
 |
 v
Health Scoring and Findings
 |
 v
JSON Report and Dashboard
```

## Project Structure

```text
repository-health-analyzer/
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── repository_routes.py
│   └── services/
│       ├── github_service.py
│       ├── structure_analyzer.py
│       ├── dependency_analyzer.py
│       ├── activity_analyzer.py
│       └── health_scorer.py
├── frontend/
│   └── app.py
├── tests/
│   └── test_main.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

* Python 3.11 or a compatible Python version
* Git
* Internet access for public GitHub repository analysis

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd repository-health-analyzer
```

Replace the placeholder with the URL of your own GitHub repository.

### 2. Create a virtual environment

**Windows PowerShell:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt or follow the appropriate Python virtual-environment activation instructions for your system.

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Start the backend

In the first terminal, run:

```powershell
python -m uvicorn backend.main:app --reload
```

The API runs at:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

### 5. Start the dashboard

Open a second terminal, activate the same virtual environment, and run:

```powershell
python -m streamlit run frontend/app.py
```

Open the local dashboard URL printed in the terminal, usually:

`http://localhost:8501`

### 6. Analyze a repository

Enter a public GitHub repository URL, for example:

`https://github.com/psf/requests`

The dashboard displays the repository overview, health score, structural findings, detected dependency files, CI/CD workflows, and recent activity.

## API Usage

### Endpoint

```http
GET /repositories/analyze?url=https://github.com/psf/requests
```

### Example request

```bash
curl "http://127.0.0.1:8000/repositories/analyze?url=https://github.com/psf/requests"
```

### Response sections

* `repository`: basic GitHub repository metadata.
* `structure_analysis`: root files, directories, structural checks, and workflow information.
* `dependency_analysis`: detected manifests and lockfiles.
* `activity_analysis`: commit counts, latest commit date, and estimated activity status.
* `health_report`: score, rating, findings, and recommendations.

## Health Scoring

The current score uses five structural indicators:

| Criterion                |  Weight |
| ------------------------ | ------: |
| README documentation     |      20 |
| Tests directory          |      25 |
| Dependency manifest      |      20 |
| Git ignore configuration |      15 |
| CI configuration         |      20 |
| **Total**                | **100** |

Each criterion contributes its weight when its corresponding check passes.

The rating is derived from the total score. A high score indicates that the repository contains the assessed structural indicators; it does not establish that the code is correct, secure, well-tested, or actively maintained.

## Running Tests

Run the automated test suite from the project root:

```powershell
python -m pytest -v
```

The tests cover health-scoring behavior, API endpoints, repository URL validation, workflow detection, and commit activity handling.

## Current Limitations

* Only public GitHub repositories are supported by the current workflow.
* Activity analysis examines up to 100 commits, not the repository's complete history.
* Dependency analysis detects manifest files but does not resolve package versions or scan for known vulnerabilities.
* CI/CD analysis detects workflow configuration files but does not execute workflows or verify their latest run status.
* Structural checks do not inspect code complexity, maintainability, or test coverage.
* Analysis depends on GitHub API availability and rate limits.
* The health score is a heuristic and should not be interpreted as an industry-standard quality rating.

## Potential Future Improvements

* Cache API responses to reduce repeated requests and GitHub API usage.
* Store analysis history in PostgreSQL.
* Add code-quality and test-coverage metrics.
* Integrate dependency vulnerability scanning.
* Analyze CI workflow run results.
* Add asynchronous analysis for improved responsiveness.
* Introduce more comprehensive unit and integration tests.
* Add Docker and CI pipelines for reproducible deployment.
* Improve scoring calibration and provide evidence for each finding.

