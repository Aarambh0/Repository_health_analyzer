
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.health_scorer import calculate_health_score

client = TestClient(app)


def test_all_checks_pass():
    structure_analysis = {
        "checks": {
            "has_readme": True,
            "has_tests_directory": True,
            "has_dependency_file": True,
            "has_gitignore": True,
            "has_ci_configuration": True,
        }
    }

    result = calculate_health_score(structure_analysis)

    assert result["score"] == 100
    assert result["max_score"] == 100
    assert result["rating"] == "Good"
    assert result["passed_checks"] == 5


def test_all_checks_fail():
    structure_analysis = {
        "checks": {
            "has_readme": False,
            "has_tests_directory": False,
            "has_dependency_file": False,
            "has_gitignore": False,
            "has_ci_configuration": False,
        }
    }

    result = calculate_health_score(structure_analysis)

    assert result["score"] == 0
    assert result["rating"] == "Poor"
    assert result["passed_checks"] == 0
    assert len(result["findings"]) == 5


def test_missing_checks_are_treated_as_failed():
    result = calculate_health_score({"checks": {}})

    assert result["score"] == 0
    assert result["passed_checks"] == 0
    assert all(
        finding["status"] == "missing"
        for finding in result["findings"]
    )


def test_home_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_invalid_repository_url():
    response = client.get(
        "/repositories/analyze",
        params={"url": "https://example.com/not-a-repository"},
    )

    assert response.status_code == 400
    assert "Invalid GitHub repository URL" in response.json()["detail"]


from unittest.mock import Mock, patch

from backend.services.structure_analyzer import (
    analyze_repository_structure,
)


@patch("backend.services.structure_analyzer.requests.get")
def test_ci_workflows_are_detected(mock_get):
    root_response = Mock()
    root_response.status_code = 200
    root_response.json.return_value = [
        {"name": ".github", "type": "dir"},
        {"name": "README.md", "type": "file"},
        {"name": "requirements-dev.txt", "type": "file"},
    ]
    root_response.raise_for_status.return_value = None

    workflow_response = Mock()
    workflow_response.status_code = 200
    workflow_response.json.return_value = [
        {"name": "run-tests.yml", "type": "file"},
        {"name": "lint.yaml", "type": "file"},
        {"name": "notes.txt", "type": "file"},
        {"name": "subfolder", "type": "dir"},
    ]
    workflow_response.raise_for_status.return_value = None

    mock_get.side_effect = [root_response, workflow_response]

    result = analyze_repository_structure("example", "project")

    assert result["checks"]["has_ci_configuration"] is True
    assert result["ci_analysis"]["has_workflow"] is True
    assert result["ci_analysis"]["workflow_count"] == 2
    assert result["ci_analysis"]["workflow_files"] == [
        "lint.yaml",
        "run-tests.yml",
    ]


@patch("backend.services.structure_analyzer.requests.get")
def test_github_directory_without_workflows(mock_get):
    root_response = Mock()
    root_response.status_code = 200
    root_response.json.return_value = [
        {"name": ".github", "type": "dir"},
        {"name": "README.md", "type": "file"},
    ]
    root_response.raise_for_status.return_value = None

    workflow_response = Mock()
    workflow_response.status_code = 404
    workflow_response.raise_for_status.return_value = None

    mock_get.side_effect = [root_response, workflow_response]

    result = analyze_repository_structure("example", "project")

    assert result["checks"]["has_ci_configuration"] is False
    assert result["ci_analysis"]["has_workflow"] is False
    assert result["ci_analysis"]["workflow_count"] == 0


from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

from backend.services.activity_analyzer import (
    analyze_repository_activity,
)


@patch("backend.services.activity_analyzer.requests.get")
def test_activity_analyzer_counts_recent_commits(mock_get):
    now = datetime.now(timezone.utc)

    recent_date = (
        now - timedelta(days=5)
    ).isoformat().replace("+00:00", "Z")

    old_date = (
        now - timedelta(days=120)
    ).isoformat().replace("+00:00", "Z")

    response = Mock()
    response.status_code = 200
    response.json.return_value = [
        {
            "commit": {
                "committer": {"date": recent_date},
                "author": {"date": recent_date},
            }
        },
        {
            "commit": {
                "committer": {"date": old_date},
                "author": {"date": old_date},
            }
        },
    ]
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    result = analyze_repository_activity("example", "project")

    assert result["commits_analyzed"] == 2
    assert result["commits_with_dates"] == 2
    assert result["commits_in_period"] == 1
    assert result["activity_status"] == "Recently active"
    assert result["days_since_latest_commit"] <= 5


@patch("backend.services.activity_analyzer.requests.get")
def test_activity_analyzer_handles_empty_commit_history(mock_get):
    response = Mock()
    response.status_code = 200
    response.json.return_value = []
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    result = analyze_repository_activity("example", "empty-project")

    assert result["commits_analyzed"] == 0
    assert result["commits_with_dates"] == 0
    assert result["commits_in_period"] == 0
    assert result["latest_commit_date"] is None
    assert result["days_since_latest_commit"] is None
    assert result["activity_status"] == "Unknown"


@patch("backend.services.activity_analyzer.requests.get")
def test_activity_analyzer_handles_missing_commit_dates(mock_get):
    response = Mock()
    response.status_code = 200
    response.json.return_value = [
        {"commit": {"committer": {}, "author": {}}},
        {"commit": {"committer": {}, "author": {}}},
    ]
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    result = analyze_repository_activity("example", "project")

    assert result["commits_analyzed"] == 2
    assert result["commits_with_dates"] == 0
    assert result["latest_commit_date"] is None
    assert result["activity_status"] == "Unknown"


@patch("backend.services.activity_analyzer.requests.get")
def test_activity_analyzer_handles_not_found_repository(mock_get):
    response = Mock()
    response.status_code = 404
    mock_get.return_value = response

    try:
        analyze_repository_activity("example", "missing-project")
        assert False, "Expected ValueError for a missing repository"
    except ValueError as exc:
        assert "not found" in str(exc).lower()


@patch("backend.services.activity_analyzer.requests.get")
def test_activity_analyzer_handles_rate_limit(mock_get):
    response = Mock()
    response.status_code = 403
    response.headers = {"X-RateLimit-Remaining": "0"}
    mock_get.return_value = response

    try:
        analyze_repository_activity("example", "project")
        assert False, "Expected ValueError for rate limiting"
    except ValueError as exc:
        assert "rate limit" in str(exc).lower()


@patch("backend.services.activity_analyzer.requests.get")
def test_activity_analyzer_handles_timeout(mock_get):
    import requests

    mock_get.side_effect = requests.exceptions.Timeout(
        "Request timed out"
    )

    try:
        analyze_repository_activity("example", "project")
        assert False, "Expected ValueError for timeout"
    except ValueError as exc:
        assert "timed out" in str(exc).lower()


@patch("backend.services.activity_analyzer.requests.get")
def test_activity_analyzer_rejects_invalid_recent_days(mock_get):
    try:
        analyze_repository_activity(
            "example",
            "project",
            recent_days=0,
        )
        assert False, "Expected ValueError for invalid recent_days"
    except ValueError as exc:
        assert "greater than zero" in str(exc).lower()

    mock_get.assert_not_called() 