
def analyze_dependencies(structure_analysis: dict) -> dict:
    """Detect dependency manifest files in the repository root."""

    root_files = {
        name.lower()
        for name in structure_analysis.get("root_files", [])
    }

    manifest_types = {
        "requirements.txt": "Python requirements",
        "requirements-dev.txt": "Python development requirements",
        "pyproject.toml": "Python project configuration",
        "poetry.lock": "Poetry lockfile",
        "pipfile": "Pipenv dependency manifest",
        "pipfile.lock": "Pipenv lockfile",
        "package.json": "Node.js dependencies",
        "package-lock.json": "npm lockfile",
        "yarn.lock": "Yarn lockfile",
        "pnpm-lock.yaml": "pnpm lockfile",
        "pom.xml": "Maven dependencies",
        "build.gradle": "Gradle dependencies",
        "build.gradle.kts": "Gradle Kotlin DSL dependencies",
        "cargo.toml": "Rust dependencies",
        "cargo.lock": "Rust lockfile",
        "go.mod": "Go dependencies",
        "go.sum": "Go dependency checksums",
    }

    detected_manifests = [
        {"file": filename, "type": description}
        for filename, description in manifest_types.items()
        if filename in root_files
    ]

    return {
        "manifest_count": len(detected_manifests),
        "detected_manifests": detected_manifests,
        "has_dependency_manifest": bool(detected_manifests),
        "note": (
            "This detects dependency manifests and lockfiles. "
            "It does not inspect package versions or vulnerabilities."
        ),
    }