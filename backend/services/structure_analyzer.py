
import requests

GITHUB_API_URL = "https://api.github.com"

TEST_DIRECTORY_NAMES = {
    "test",
    "tests",
    "__tests__",
    "spec",
    "specs",
}

TEST_FILE_SUFFIXES = (
    ".test.js",
    ".test.jsx",
    ".test.ts",
    ".test.tsx",
    ".spec.js",
    ".spec.jsx",
    ".spec.ts",
    ".spec.tsx",
    "test.java",
    "tests.java",
    "test.py",
)

TEST_FILE_PREFIXES = (
    "test_",
    "test.",
)


def _get_directory_contents(
    owner: str,
    repo: str,
    path: str,
    headers: dict,
) -> list:
    """Fetch directory contents from the GitHub Contents API."""

    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/contents"

    if path:
        url = f"{url}/{path}"

    response = requests.get(
        url,
        headers=headers,
        timeout=10,
    )

    # Treat a missing optional directory as empty.
    if response.status_code == 404:
        return []

    response.raise_for_status()
    items = response.json()

    if not isinstance(items, list):
        return []

    return items


def _is_test_file(filename: str) -> bool:
    """Recognize common Python, Java, and JavaScript test filenames."""

    name = filename.lower()

    return (
        name.startswith(TEST_FILE_PREFIXES)
        or name.endswith(TEST_FILE_SUFFIXES)
    )


def _scan_for_tests(
    owner: str,
    repo: str,
    directory_path: str,
    headers: dict,
    max_depth: int = 6,
    current_depth: int = 0,
) -> tuple[list[str], list[str]]:
    """Find conventional test directories and test files recursively."""

    if current_depth >= max_depth:
        return [], []

    items = _get_directory_contents(
        owner,
        repo,
        directory_path,
        headers,
    )

    test_paths = []
    test_files = []

    for item in items:
        name = item.get("name", "")
        item_type = item.get("type")
        item_path = f"{directory_path}/{name}"

        if item_type == "dir":
            if name.lower() in TEST_DIRECTORY_NAMES:
                test_paths.append(item_path)

            nested_paths, nested_files = _scan_for_tests(
                owner,
                repo,
                item_path,
                headers,
                max_depth=max_depth,
                current_depth=current_depth + 1,
            )

            test_paths.extend(nested_paths)
            test_files.extend(nested_files)

        elif item_type == "file" and _is_test_file(name):
            test_files.append(item_path)

    return sorted(set(test_paths)), sorted(set(test_files))


def analyze_repository_structure(owner: str, repo: str) -> dict:
    """Analyze repository structure, test indicators, and CI workflows."""

    headers = {
        "Accept": "application/vnd.github+json",
    }

    # Fetch repository root contents.
    root_items = _get_directory_contents(
        owner,
        repo,
        "",
        headers,
    )

    root_files = {
        item["name"].lower()
        for item in root_items
        if item.get("type") == "file"
    }

    root_directories = {
        item["name"].lower()
        for item in root_items
        if item.get("type") == "dir"
    }

    # Preserve original directory names for API paths.
    root_directory_names = {
        item["name"].lower(): item["name"]
        for item in root_items
        if item.get("type") == "dir"
    }

    # Detect conventional test directories at the repository root.
    detected_test_paths = sorted(
        root_directory_names[name]
        for name in root_directories
        if name in TEST_DIRECTORY_NAMES
    )

    # Scan source directories for nested test locations.
    source_paths = []

    if "src" in root_directory_names:
        source_paths.append(root_directory_names["src"])

    if "app" in root_directory_names:
        app_path = root_directory_names["app"]

        app_items = _get_directory_contents(
            owner,
            repo,
            app_path,
            headers,
        )

        for item in app_items:
            if (
                item.get("type") == "dir"
                and item.get("name", "").lower() == "src"
            ):
                source_paths.append(
                    f"{app_path}/{item['name']}"
                )

    detected_test_files = sorted(
        filename
        for filename in root_files
        if _is_test_file(filename)
    )

    for source_path in source_paths:
        nested_paths, nested_files = _scan_for_tests(
            owner,
            repo,
            source_path,
            headers,
        )

        detected_test_paths.extend(nested_paths)
        detected_test_files.extend(nested_files)

    detected_test_paths = sorted(set(detected_test_paths))
    detected_test_files = sorted(set(detected_test_files))

    has_tests = bool(
        detected_test_paths or detected_test_files
    )

    # Check for actual GitHub Actions workflow files.
    has_ci_workflow = False
    workflow_files = []

    if ".github" in root_directory_names:
        github_path = root_directory_names[".github"]
        workflow_path = f"{github_path}/workflows"

        workflow_items = _get_directory_contents(
            owner,
            repo,
            workflow_path,
            headers,
        )

        workflow_files = sorted(
            item["name"]
            for item in workflow_items
            if item.get("type") == "file"
            and item.get("name", "").lower().endswith(
                (".yml", ".yaml")
            )
        )

        has_ci_workflow = bool(workflow_files)

    # Evaluate repository structure indicators.
    checks = {
        "has_readme": any(
            name.startswith("readme")
            for name in root_files
        ),
        "has_tests_directory": has_tests,
        "has_dependency_file": bool(
            root_files.intersection({
                "requirements.txt",
                "requirements-dev.txt",
                "pyproject.toml",
                "poetry.lock",
                "pipfile",
                "pipfile.lock",
                "package.json",
                "package-lock.json",
                "yarn.lock",
                "pnpm-lock.yaml",
                "pom.xml",
                "build.gradle",
                "build.gradle.kts",
                "cargo.toml",
                "cargo.lock",
                "go.mod",
                "go.sum",
            })
        ),
        "has_gitignore": ".gitignore" in root_files,
        "has_ci_configuration": has_ci_workflow,
    }

    return {
        "root_file_count": len(root_files),
        "root_directory_count": len(root_directories),
        "root_files": sorted(root_files),
        "root_directories": sorted(root_directories),
        "checks": checks,
        "test_analysis": {
            "has_tests": has_tests,
            "detected_test_paths": detected_test_paths,
            "detected_test_files": detected_test_files,
            "note": (
                "Test detection uses common directory and filename "
                "conventions. It does not confirm that tests exist "
                "in every framework-specific location or that they pass."
            ),
        },
        "ci_analysis": {
            "has_workflow": has_ci_workflow,
            "workflow_count": len(workflow_files),
            "workflow_files": workflow_files,
        },
    }