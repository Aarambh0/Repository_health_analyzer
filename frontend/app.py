
import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Repository Health Analyzer",
    page_icon="🔍",
    layout="wide",
)

# --------------------------------------------------
# Dashboard Header
# --------------------------------------------------

st.title("🔍 Repository Health Analyzer")

st.write(
    "Analyze a public GitHub repository's structure, "
    "dependency manifests, CI/CD workflows, recent activity, "
    "and preliminary health score."
)

st.info(
    "The current health score evaluates repository structure indicators. "
    "It is not a complete code-quality or security audit."
)

# --------------------------------------------------
# Repository Input
# --------------------------------------------------

repository_url = st.text_input(
    "GitHub Repository URL",
    placeholder="https://github.com/psf/requests",
)

if st.button("Analyze Repository", type="primary"):

    if not repository_url.strip():
        st.warning("Please enter a GitHub repository URL.")

    else:
        try:
            with st.spinner("Analyzing repository..."):
                response = requests.get(
                    f"{API_URL}/repositories/analyze",
                    params={"url": repository_url.strip()},
                    timeout=90,
                )

            # --------------------------------------------------
            # Handle Successful API Response
            # --------------------------------------------------

            if response.status_code == 200:
                result = response.json()

                repository = result["repository"]
                structure = result["structure_analysis"]
                dependencies = result["dependency_analysis"]
                activity = result["activity_analysis"]
                report = result["health_report"]

                ci_analysis = structure.get(
                    "ci_analysis",
                    {
                        "has_workflow": False,
                        "workflow_count": 0,
                        "workflow_files": [],
                    },
                )

                # --------------------------------------------------
                # Repository Information
                # --------------------------------------------------

                st.success(result["message"])
                st.subheader(repository["full_name"])

                st.write(
                    repository.get("description")
                    or "No description available."
                )

                st.markdown(
                    f"[View Repository on GitHub]"
                    f"({repository['html_url']})"
                )

                st.write(
                    f"**Primary language:** "
                    f"{repository.get('language') or 'Not specified'}"
                )

                st.write(
                    f"**Default branch:** {repository['default_branch']}"
                )

                # --------------------------------------------------
                # Repository Overview
                # --------------------------------------------------

                st.subheader("Repository Overview")

                col1, col2, col3, col4 = st.columns(4)

                col1.metric(
                    "Health Score",
                    f"{report['score']}/{report['max_score']}",
                )
                col2.metric("Stars", repository["stars"])
                col3.metric("Forks", repository["forks"])
                col4.metric("Open Issues", repository["open_issues"])

                # --------------------------------------------------
                # Health Report
                # --------------------------------------------------

                st.subheader("Repository Health")

                st.write(f"**Rating:** {report['rating']}")

                score = report["score"]
                max_score = report["max_score"]

                if max_score > 0:
                    st.progress(score / max_score)

                st.write(
                    f"Passed {report['passed_checks']} of "
                    f"{report['total_checks']} structural checks."
                )

                # --------------------------------------------------
                # Findings and Recommendations
                # --------------------------------------------------

                st.subheader("Findings and Recommendations")

                for finding in report["findings"]:
                    if finding["status"] == "passed":
                        st.success(
                            f"✓ {finding['name']} "
                            f"({finding['weight']} points)"
                        )
                    else:
                        st.warning(
                            f"⚠ {finding['name']} — "
                            f"{finding['recommendation']}"
                        )

                # --------------------------------------------------
                # Repository Activity
                # --------------------------------------------------

                st.subheader("Repository Activity")

                st.caption(
                    f"Activity window: the last {activity['recent_days']} days"
                )

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Commits in Period",
                    activity["commits_in_period"],
                )

                col2.metric(
                    "Days Since Latest Commit",
                    (
                        activity["days_since_latest_commit"]
                        if activity["days_since_latest_commit"] is not None
                        else "Unknown"
                    ),
                )

                col3.metric(
                    "Activity Status",
                    activity["activity_status"],
                )

                st.write(
                    f"**Commits analyzed:** "
                    f"{activity['commits_analyzed']}"
                )

                st.write(
                    f"**Commits with dates:** "
                    f"{activity['commits_with_dates']}"
                )

                st.write(
                    f"**Latest commit date:** "
                    f"{activity['latest_commit_date'] or 'Unknown'}"
                )

                st.caption(activity["note"])

                # --------------------------------------------------
                # Dependency Analysis
                # --------------------------------------------------

                st.subheader("Dependency Analysis")

                st.metric(
                    "Dependency Files Detected",
                    dependencies["manifest_count"],
                )

                detected_manifests = dependencies["detected_manifests"]

                if detected_manifests:
                    st.dataframe(
                        detected_manifests,
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.info(
                        "No recognized dependency manifests "
                        "were found in the repository root."
                    )

                st.caption(dependencies["note"])

                # --------------------------------------------------
                # CI/CD Workflow Analysis
                # --------------------------------------------------

                st.subheader("CI/CD Workflow Analysis")

                if ci_analysis["has_workflow"]:
                    st.success(
                        f"Detected {ci_analysis['workflow_count']} "
                        "GitHub Actions workflow file(s)."
                    )

                    st.dataframe(
                        [
                            {"Workflow File": filename}
                            for filename in ci_analysis["workflow_files"]
                        ],
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.warning(
                        "No GitHub Actions workflow files were detected "
                        "in .github/workflows/."
                    )

                st.caption(
                    "This checks for workflow configuration files; "
                    "it does not verify whether the workflows execute "
                    "successfully."
                )

                # --------------------------------------------------
                # Repository Structure Details
                # --------------------------------------------------

                with st.expander("Repository Structure Details"):

                    col1, col2 = st.columns(2)

                    col1.metric(
                        "Root Files",
                        structure["root_file_count"],
                    )

                    col2.metric(
                        "Root Directories",
                        structure["root_directory_count"],
                    )

                    st.markdown("**Root Files**")

                    st.code(
                        "\n".join(structure["root_files"]) or "None",
                        language="text",
                    )

                    st.markdown("**Root Directories**")

                    st.code(
                        "\n".join(structure["root_directories"]) or "None",
                        language="text",
                    )

                    st.markdown("**Structural Checks**")

                    for check_name, passed in structure["checks"].items():
                        if passed:
                            st.write(
                                f"✓ {check_name.replace('_', ' ').title()}"
                            )
                        else:
                            st.write(
                                f"✗ {check_name.replace('_', ' ').title()}"
                            )

                # --------------------------------------------------
                # Scoring Disclaimer
                # --------------------------------------------------

                st.divider()
                st.caption(report["scoring_note"])

            # --------------------------------------------------
            # Handle API Errors
            # --------------------------------------------------

            else:
                try:
                    error_data = response.json()
                    detail = error_data.get(
                        "detail",
                        "The analysis request failed.",
                    )
                except ValueError:
                    detail = "The analysis request failed."

                st.error(f"Analysis failed: {detail}")

        # --------------------------------------------------
        # Handle Connection and Request Errors
        # --------------------------------------------------

        except requests.exceptions.ConnectionError:
            st.error(
                "Cannot connect to the backend. "
                "Start the FastAPI server first."
            )

        except requests.exceptions.Timeout:
            st.error(
                "The analysis took too long. Please try again."
            )

        except requests.exceptions.RequestException as exc:
            st.error(f"Request error: {exc}")

        except (KeyError, TypeError, ValueError):
            st.error(
                "The backend returned an unexpected response. "
                "Check that the API is running the latest code."
            )