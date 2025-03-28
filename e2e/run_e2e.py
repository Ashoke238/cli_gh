# run_e2e.py

import sys
import os
import time
import requests
from e2e.e2e_validator import run_e2e_validation
from cli.logger import setup_logger

logger = setup_logger()

def wait_for_github_pipeline_completion(repo_name, branch="dev", max_wait=1500, poll_interval=60):
    """
    Polls GitHub Actions for the latest workflow run in the given repo and branch until it's completed.
    """
    logger.info(f"🔄 Checking workflow status in repo: {repo_name} (branch: {branch})")
    headers = {
        "Authorization": f"token {os.getenv('GH_TOKEN')}",
        "Accept": "application/vnd.github+json"
    }
    url = f"https://api.github.com/repos/Ashoke238/{repo_name}/actions/runs"

    waited = 0
    while waited < max_wait:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        runs = response.json().get("workflow_runs", [])

        # Filter for dev branch run
        dev_runs = [run for run in runs if run["head_branch"] == branch]
        if not dev_runs:
            logger.warning("⚠️ No workflow runs found for branch 'dev'. Retrying...")
            time.sleep(poll_interval)
            waited += poll_interval
            continue

        latest_run = dev_runs[0]
        status = latest_run["status"]
        conclusion = latest_run.get("conclusion")

        logger.info(f"⏳ Latest workflow status: {status} (conclusion: {conclusion})")

        if status == "completed":
            if conclusion != "success":
                logger.warning(f"⚠️ Workflow run completed but with conclusion: {conclusion}. Proceeding with validation anyway.")
            else:
                logger.info("✅ Workflow run completed successfully.")
            return

        time.sleep(poll_interval)
        waited += poll_interval

    logger.warning("⚠️ Workflow run did not complete within wait time. Proceeding anyway.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Please provide the GitHub repo name.")
        sys.exit(1)

    repo_name = sys.argv[1]
    logger.info(f"🚀 Starting E2E validation for repo: {repo_name}")

    # Step 1: Wait for workflow to finish in new repo
    wait_for_github_pipeline_completion(repo_name)

    # Step 2: Run E2E Validation
    report_path = run_e2e_validation(repo_name)
    logger.info(f"✅ Report generated at: {report_path}")
    print(f"✅ Report generated at {report_path}")
