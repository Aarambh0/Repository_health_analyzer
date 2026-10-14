
from datetime import datetime, timezone

import requests

GITHUB_API_URL = "https://api.github.com"


def analyze_repository_activity(
    owner: str,
    repo: str,
    recent_days: int = 90,
) -> dict:
    """
    Analyze recent commit activity for a public GitHub repository.

    Examines up to 100 commits from the repository's default branch.
    """

    if recent_days <= 0:
        raise ValueError("recent_days must be greater than zero.")

    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/commits"

    try:
        response = requests.get(
            url,
            headers={"Accept": "application/vnd.github+json"},
            params={"per_page": 100},
            timeout=15,
        )

        if response.status_code == 404:
            raise ValueError(
                "Repository or commit history not found."
            )

        if response.status_code == 403:
            remaining = response.headers.get("X-RateLimit-Remaining")

            if remaining == "0":
                raise ValueError(
                    "GitHub API rate limit reached. Try again later."
                )

            raise ValueError(
                "GitHub API access denied."
            )

        response.raise_for_status()

    except requests.exceptions.Timeout as exc:
        raise ValueError(
            "GitHub activity request timed out."
        ) from exc

    except requests.exceptions.ConnectionError as exc:
        raise ValueError(
            "Unable to connect to GitHub to retrieve activity."
        ) from exc

    commits = response.json()

    if not isinstance(commits, list):
        raise ValueError(
            "Unexpected response from GitHub commits API."
        )

    now = datetime.now(timezone.utc)
    cutoff = now.timestamp() - recent_days * 24 * 60 * 60

    commit_dates = []

    for commit_item in commits:
        if not isinstance(commit_item, dict):
            continue

        commit_data = commit_item.get("commit") or {}

        if not isinstance(commit_data, dict):
            continue

        committer = commit_data.get("committer") or {}
        author = commit_data.get("author") or {}

        if not isinstance(committer, dict):
            committer = {}

        if not isinstance(author, dict):
            author = {}

        date_string = (
            committer.get("date")
            or author.get("date")
        )

        if not isinstance(date_string, str) or not date_string:
            continue

        try:
            commit_date = datetime.fromisoformat(
                date_string.replace("Z", "+00:00")
            )
        except ValueError:
            continue

        if commit_date.tzinfo is None:
            commit_date = commit_date.replace(
                tzinfo=timezone.utc
            )

        commit_dates.append(commit_date)

    recent_commits = [
        date
        for date in commit_dates
        if date.timestamp() >= cutoff
    ]

    latest_commit = max(commit_dates) if commit_dates else None

    if latest_commit is None:
        activity_status = "Unknown"
        days_since_latest_commit = None
    else:
        days_since_latest_commit = max(
            0,
            (now - latest_commit).days,
        )

        if days_since_latest_commit <= 30:
            activity_status = "Recently active"
        elif days_since_latest_commit <= 90:
            activity_status = "Some recent activity"
        else:
            activity_status = "No recent commit activity"

    return {
        "recent_days": recent_days,
        "commits_analyzed": len(commits),
        "commits_with_dates": len(commit_dates),
        "commits_in_period": len(recent_commits),
        "latest_commit_date": (
            latest_commit.isoformat()
            if latest_commit
            else None
        ),
        "days_since_latest_commit": days_since_latest_commit,
        "activity_status": activity_status,
        "note": (
            "Activity is estimated from up to 100 commits on the "
            "default branch. It is not a complete measure of project "
            "maintenance, and commit author dates may differ from "
            "commit dates."
        ),
    }