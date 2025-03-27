import os
from github import Github
from dotenv import load_dotenv
from git import Repo
import shutil
from logger import setup_logger
from dotenv import load_dotenv
from logger import setup_logger

load_dotenv()
logger = setup_logger()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
TEMPLATE_REPO = "https://github.com/Ashoke238/model_train_infer.git"

def validate_repo_availability(repo_name):
    g = Github(GITHUB_TOKEN)
    user = g.get_user(GITHUB_USERNAME)

    logger.info(f"Checking GitHub if repository '{repo_name}' exists...")

    try:
        repo = user.get_repo(repo_name)
        if repo:
            raise ValueError(f"❌ GitHub repository '{repo_name}' already exists.")
    except Exception as e:
        if "Not Found" in str(e):
            logger.info(f"✅ Repository '{repo_name}' is available.")
        else:
            logger.error(f"GitHub validation error: {e}")
            raise ValueError(f"GitHub validation error: {e}")

def create_and_setup_repo(repo_name):
    g = Github(GITHUB_TOKEN)
    user = g.get_user(GITHUB_USERNAME)

    logger.info(f"Creating GitHub repository '{repo_name}'...")

    try:
        new_repo = user.create_repo(repo_name)
        if repo:
            logger.info(f"✅ Repository '{repo_name}' created successfully.")
    except Exception as e:
        logger.error(f"GitHub repository creation error: {e}")
        raise ValueError(f"GitHub repository creation error: {e}")

    # Clone template locally
    clone_dir = f"/tmp/{repo_name}"
    logger.info(f"Cloning template repo into {clone_dir}...")
    Repo.clone_from(TEMPLATE_REPO, clone_dir)

    # Set remote URL to new repo and push
    repo = Repo(clone_dir)
    origin = repo.create_remote('new_origin', new_repo.clone_url.replace(
        'https://', f'https://{GITHUB_TOKEN}@'))
    repo.git.push('--all', 'new_origin')
    logger.info(f"✅ Pushed template code to '{repo_name}'.")

     # Create dev branch
    repo.git.checkout('-b', 'dev')
    repo.git.push('--set-upstream', 'new_origin', 'dev')
    logger.info(f"✅ Created 'dev' branch and pushed to '{repo_name}'.")

     # Cleanup cloned directory
    shutil.rmtree(clone_dir)

    return new_repo.clone_url