
import re

from fastapi import APIRouter, HTTPException

from backend.services.github_service import get_repository_info
from backend.services.structure_analyzer import analyze_repository_structure
from backend.services.health_scorer import calculate_health_score
from backend.services.dependency_analyzer import analyze_dependencies
from backend.services.activity_analyzer import analyze_repository_activity

router = APIRouter(
    prefix="/repositories",
    tags=["Repositories"],
)


@router.get("/analyze")
def analyze_repository(url: str):
    """Analyze a public GitHub repository and return its health report."""

    pattern = r"^https?://github\.com/([^/]+)/([^/]+)/?$"
    match = re.match(pattern, url.strip())

    if not match:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid GitHub repository URL. "
                "Use https://github.com/owner/repository"
            ),
        )

    owner, repo = match.groups()
    repo = repo.removesuffix(".git")

    try:
        repository_info = get_repository_info(owner, repo)
        structure_info = analyze_repository_structure(owner, repo)
        health_report = calculate_health_score(structure_info)
        dependency_report = analyze_dependencies(structure_info)
        activity_report = analyze_repository_activity(owner, repo)

        return {
            "message": "Repository analysis completed successfully.",
            "repository": repository_info,
            "structure_analysis": structure_info,
            "dependency_analysis": dependency_report,
            "activity_analysis": activity_report,
            "health_report": health_report,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "Unable to complete repository analysis. "
                "Check GitHub availability and try again."
            ),
        ) from exc