import os
import json
import requests
import zipfile
import tempfile
from github import Github
from github.GithubException import GithubException
from dotenv import load_dotenv
from logger import setup_logger

load_dotenv()
logger = setup_logger()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
TEMPLATE_REPO_ZIP_URL = "https://github.com/Ashoke238/model_train_infer/archive/refs/heads/main.zip"

def validate_repo_availability(repo_name):
    g = Github(GITHUB_TOKEN)
    user = g.get_user()
    try:
        user.get_repo(repo_name)
        raise Exception(f"Repository '{repo_name}' already exists.")
    except GithubException as e:
        if e.status != 404:
            raise e
    logger.info(f"✅ Repository '{repo_name}' is available.")

def create_github_repo(repo_name):
    g = Github(GITHUB_TOKEN)
    user = g.get_user()
    repo = user.create_repo(repo_name, private=True, auto_init=True)
    logger.info(f"✅ Created repository '{repo_name}' with auto-initialized 'main' branch.")
    return repo

def download_and_extract_template():
    tmp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(tmp_dir, "template_repo.zip")
    
    response = requests.get(TEMPLATE_REPO_ZIP_URL)
    response.raise_for_status()

    with open(zip_path, "wb") as f:
        f.write(response.content)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(tmp_dir)

    extracted_contents = os.listdir(tmp_dir)
    for item in extracted_contents:
        item_path = os.path.join(tmp_dir, item)
        if os.path.isdir(item_path):
            return item_path
    raise Exception("No extracted folder found after downloading template.")

def push_files_to_repo(repo, local_folder, branch="main"):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(repo.full_name)

    existing_files = {content.path for content in repo.get_contents("", ref=branch)}

    for root, _, files in os.walk(local_folder):
        for file in files:
            local_file_path = os.path.join(root, file)
            repo_file_path = os.path.relpath(local_file_path, local_folder).replace("\\", "/")

            if repo_file_path in existing_files:
                continue  # Skip already existing files like README.md

            with open(local_file_path, 'rb') as f:
                content = f.read()

            repo.create_file(
                path=repo_file_path,
                message=f"Add {repo_file_path}",
                content=content,
                branch=branch
            )

    logger.info("✅ Template files uploaded successfully.")

def create_dev_branch(repo_name, base_branch="main", new_branch="dev"):
    g = Github(GITHUB_TOKEN)
    repo = g.get_user().get_repo(repo_name)
    base_sha = repo.get_git_ref(f"heads/{base_branch}").object.sha
    repo.create_git_ref(ref=f"refs/heads/{new_branch}", sha=base_sha)
    logger.info(f"✅ Branch '{new_branch}' created from '{base_branch}'.")

def create_and_setup_repo(repo_name):
    validate_repo_availability(repo_name)
    
    # Creates repo with main initialized clearly
    repo = create_github_repo(repo_name)
    
    # Downloads & uploads all files to main clearly
    local_folder = download_and_extract_template()
    push_files_to_repo(repo, local_folder)

    # Creates dev branch only after main is fully populated
    create_dev_branch(repo_name)

    return repo.clone_url

def update_config_json(repo_name, train_job_id, infer_job_id, branch="dev"):
    g = Github(GITHUB_TOKEN)
    repo = g.get_user().get_repo(repo_name)
    file_path = "mlops_config/mlops_config_dev.json"
    logger.info(f"Updating '{file_path}' with new job IDs...")

    #get the contents of the file

    contents = repo.get_contents(file_path, ref=branch)
    #log the contents of the file
    logger.info(f"Contents of the file: {contents.decoded_content.decode('utf-8')}")
    config_json = json.loads(contents.decoded_content.decode('utf-8'))
    config_json["train_job_id"] = train_job_id
    config_json["infer_job_id"] = infer_job_id

    repo.update_file(
        path=file_path,
        message="Update Databricks Job IDs",
        content=json.dumps(config_json, indent=4),
        sha=contents.sha,
        branch=branch
    )
    logger.info(f"✅ '{file_path}' updated with new job IDs.")
