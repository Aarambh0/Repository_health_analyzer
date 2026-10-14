
def calculate_health_score(structure_analysis: dict) -> dict:
    """
    Calculate an initial repository health score out of 100.

    This version evaluates five repository structure indicators.
    It does not yet assess code quality, vulnerabilities, or test results.
    """

    checks = structure_analysis.get("checks", {})

    criteria = {
        "readme": {
            "label": "README documentation",
            "check": "has_readme",
            "weight": 20,
            "recommendation": "Add a README.md explaining setup and usage.",
        },
        "tests": {
            "label": "Test directory",
            "check": "has_tests_directory",
            "weight": 25,
            "recommendation": "Add automated tests in a tests directory.",
        },
        "dependencies": {
            "label": "Dependency manifest",
            "check": "has_dependency_file",
            "weight": 20,
            "recommendation": "Add a dependency manifest for reproducible setup.",
        },
        "gitignore": {
            "label": "Git ignore configuration",
            "check": "has_gitignore",
            "weight": 15,
            "recommendation": "Add a .gitignore for generated and sensitive files.",
        },
        "ci": {
            "label": "CI configuration indicator",
            "check": "has_ci_configuration",
            "weight": 20,
            "recommendation": (
                "Inspect or add a CI workflow, such as GitHub Actions."
            ),
        },
    }

    score = 0
    findings = []
    passed_checks = 0

    for criterion in criteria.values():
        check_name = criterion["check"]
        passed = checks.get(check_name, False) is True

        if passed:
            score += criterion["weight"]
            passed_checks += 1
            status = "passed"
            recommendation = None
        else:
            status = "missing"
            recommendation = criterion["recommendation"]

        findings.append({
            "name": criterion["label"],
            "status": status,
            "weight": criterion["weight"],
            "recommendation": recommendation,
        })

    if score >= 80:
        rating = "Good"
    elif score >= 60:
        rating = "Fair"
    elif score >= 40:
        rating = "Needs Improvement"
    else:
        rating = "Poor"

    return {
        "score": score,
        "max_score": 100,
        "rating": rating,
        "passed_checks": passed_checks,
        "total_checks": len(criteria),
        "findings": findings,
        "scoring_note": (
            "Preliminary structure-based score. "
            "It does not represent a complete code quality or security audit."
        ),
    }