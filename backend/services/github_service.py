
import requests


GITHUB_API_URL = "https://api.github.com"


def get_repository_info(owner: str, repo: str) -> dict:
    """
    Fetch basic information about a public GitHub repository.
    """
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}"

    response = requests.get(
        url,
        headers={"Accept": "application/vnd.github+json"},
        timeout=10,
    )

    if response.status_code == 404:
        raise ValueError("Repository not found or not publicly accessible.")

    if response.status_code == 403:
        raise ValueError("GitHub API rate limit reached or access denied.")

    response.raise_for_status()

    data = response.json()

    return {
        "name": data["name"],
        "full_name": data["full_name"],
        "description": data["description"],
        "stars": data["stargazers_count"],
        "forks": data["forks_count"],
        "open_issues": data["open_issues_count"],
        "language": data["language"],
        "default_branch": data["default_branch"],
        "html_url": data["html_url"],
    }