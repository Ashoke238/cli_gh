import os
import requests
from dotenv import load_dotenv
from cli.logger import setup_logger

load_dotenv()
logger = setup_logger()

DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN")
DATABRICKS_USERNAME = os.getenv("DATABRICKS_USERNAME")

headers = {
    'Authorization': f'Bearer {DATABRICKS_TOKEN}',
    'Content-Type': 'application/json'
}

def validate_databricks_job_availability(repo_name, branch="dev"):
    job_names = [
        f"mlops_{repo_name}_train_{branch}",
        f"mlops_{repo_name}_infer_{branch}"
    ]

    response = requests.get(
        f"{DATABRICKS_HOST}/api/2.1/jobs/list",
        headers=headers
    )

    if response.status_code != 200:
        logger.error(f"Databricks API error: {response.text}")
        raise ValueError(f"Databricks API error: {response.text}")

    existing_jobs = response.json().get("jobs", [])
    existing_job_names = [job['settings']['name'] for job in existing_jobs]

    conflicts = [job_name for job_name in job_names if job_name in existing_job_names]

    if conflicts:
        raise ValueError(f"Databricks job(s) already exist: {', '.join(conflicts)}")

    logger.info("✅ Databricks job names are available.")

def import_repo_to_databricks(git_url, repo_name):
    payload = {
        "url": git_url,
        "provider": "gitHub",
        "path": f"/Repos/{DATABRICKS_USERNAME}/{repo_name}"
    }

    response = requests.post(
        f"{DATABRICKS_HOST}/api/2.0/repos",
        json=payload,
        headers=headers
    )

    if response.status_code not in (200, 201):
        logger.error(f"Failed to import repo: {response.text}")
        raise Exception(f"Failed to import repo: {response.text}")

    repo_id = response.json().get("id")
    logger.info(f"✅ Imported GitHub repo '{repo_name}' to Databricks with Repo ID {repo_id}.")

    return repo_id

def create_job(job_json):
    response = requests.post(
        f"{DATABRICKS_HOST}/api/2.1/jobs/create",
        json=job_json,
        headers=headers
    )

    if response.status_code != 200:
        logger.error(f"Databricks Job Creation Failed: {response.text}")
        raise Exception(f"Databricks Job Creation Failed: {response.text}")

    job_id = response.json().get('job_id')
    logger.info(f"✅ Databricks job '{job_json['name']}' created successfully with Job ID {job_id}.")

    return job_id

def create_jobs(repo_name, git_url, branch="dev"):
    train_job_json = {
        "name": f"mlops_{repo_name}_train_{branch}",
        "git_source": {
            "git_url": git_url,
            "git_provider": "gitHub",
            "git_branch": branch
        },
        "tasks": [{
            "task_key": f"mlops_{repo_name}_train_{branch}",
            "run_if": "ALL_SUCCESS",
            "notebook_task": {
                "notebook_path": "notebooks/Demo_train_Notebook1",
                "source": "GIT"
            }
        }],
        "format": "MULTI_TASK",
        "trigger": {
            "periodic": {
                "interval": 30,
                "unit": "DAYS"
            }
        },
        "max_concurrent_runs": 1,
        "queue": {"enabled": True}
    }

    infer_job_json = {
        "name": f"mlops_{repo_name}_infer_{branch}",
        "git_source": {
            "git_url": git_url,
            "git_provider": "gitHub",
            "git_branch": branch
        },
        "tasks": [{
            "task_key": f"mlops_{repo_name}_infer_{branch}",
            "run_if": "ALL_SUCCESS",
            "notebook_task": {
                "notebook_path": "notebooks/Demo_inference_Notebook1",
                "source": "GIT"
            }
        }],
        "format": "MULTI_TASK",
        "trigger": {
            "periodic": {
                "interval": 1,
                "unit": "HOURS"
            }
        },
        "max_concurrent_runs": 1,
        "queue": {"enabled": True}
    }

    train_job_id = create_job(train_job_json)
    infer_job_id = create_job(infer_job_json)

    return train_job_id, infer_job_id
