import os
import json
import requests
import zipfile
import tempfile
from github import Github
from github.GithubException import GithubException
from dotenv import load_dotenv
from base64 import b64encode
from nacl import encoding, public
from cli.logger import setup_logger

# Load environment variables (locally or from GitHub Actions)
load_dotenv()
logger = setup_logger()

GH_TOKEN = os.getenv("GH_TOKEN")  # renamed from GITHUB_TOKEN
TEMPLATE_REPO_ZIP_URL = "https://github.com/Ashoke238/model_train_infer/archive/refs/heads/main.zip"


def validate_repo_availability(repo_name):
    g = Github(GH_TOKEN)
    user = g.get_user()
    try:
        user.get_repo(repo_name)
        raise Exception(f"Repository '{repo_name}' already exists.")
    except GithubException as e:
        if e.status != 404:
            raise e
    logger.info(f"✅ Repository '{repo_name}' is available.")


def create_github_repo(repo_name):
    g = Github(GH_TOKEN)
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
    g = Github(GH_TOKEN)
    repo = g.get_repo(repo.full_name)
    existing_files = {content.path for content in repo.get_contents("", ref=branch)}

    for root, _, files in os.walk(local_folder):
        for file in files:
            local_file_path = os.path.join(root, file)
            repo_file_path = os.path.relpath(local_file_path, local_folder).replace("\\", "/")

            if repo_file_path in existing_files:
                continue  # Skip existing files like README.md

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
    g = Github(GH_TOKEN)
    repo = g.get_user().get_repo(repo_name)
    base_sha = repo.get_git_ref(f"heads/{base_branch}").object.sha
    repo.create_git_ref(ref=f"refs/heads/{new_branch}", sha=base_sha)
    logger.info(f"✅ Branch '{new_branch}' created from '{base_branch}'.")


def encrypt_secret(public_key: str, secret_value: str) -> str:
    """Encrypt a secret using the GitHub repo's public key (required by GitHub)."""
    pk = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(pk)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return b64encode(encrypted).decode("utf-8")


def add_github_repo_secrets(repo_name, secrets_dict):
    """Push secrets into the newly created GitHub repo."""
    g = Github(GH_TOKEN)
    repo = g.get_user().get_repo(repo_name)

    # Get public key for secrets
    public_key_response = repo._requester.requestJsonAndCheck(
        "GET", repo.url + "/actions/secrets/public-key"
    )[1]

    public_key = public_key_response["key"]
    key_id = public_key_response["key_id"]

    for secret_name, secret_value in secrets_dict.items():
        encrypted_value = encrypt_secret(public_key, secret_value)
        repo._requester.requestJsonAndCheck(
            "PUT",
            repo.url + f"/actions/secrets/{secret_name}",
            input={
                "encrypted_value": encrypted_value,
                "key_id": key_id
            }
        )

    logger.info(f"✅ GitHub secrets added to '{repo_name}' successfully.")


def create_and_setup_repo(repo_name):
    validate_repo_availability(repo_name)
    repo = create_github_repo(repo_name)
    local_folder = download_and_extract_template()
    push_files_to_repo(repo, local_folder)
    create_dev_branch(repo_name)

    # Add secrets after dev branch is created
    username = os.getenv("DATABRICKS_USERNAME")
    secrets_dict = {
        "DATABRICKS_HOST": os.getenv("DATABRICKS_HOST"),
        "DATABRICKS_TOKEN": os.getenv("DATABRICKS_TOKEN"),
        "DATABRICKS_USERNAME": os.getenv("DATABRICKS_USERNAME"),
        "GH_TOKEN": os.getenv("GH_TOKEN"),
        "MLFLOW_USER_EMAIL": os.getenv("MLFLOW_USER_EMAIL")
    }
    for key, value in secrets_dict.items():
        logger.info(f"🔍 Secret {key}: {'✅ SET' if value else '❌ MISSING'}")
    add_github_repo_secrets(repo_name, secrets_dict)

    return repo.clone_url


def update_config_json(repo_name, train_job_id, infer_job_id, branch="dev"):
    g = Github(GH_TOKEN)
    repo = g.get_user().get_repo(repo_name)
    file_path = "mlops_config/mlops_config_dev.json"
    logger.info(f"Updating '{file_path}' with new job IDs...")

    contents = repo.get_contents(file_path, ref=branch)
    logger.info(f"Contents of the file: {contents.decoded_content.decode('utf-8')}")
    config_json = json.loads(contents.decoded_content.decode('utf-8'))

    config_json["train_job_id"] = train_job_id
    config_json["infer_job_id"] = infer_job_id
    config_json["repo_name"] = repo_name

    repo.update_file(
        path=file_path,
        message="Update Databricks Job IDs",
        content=json.dumps(config_json, indent=4),
        sha=contents.sha,
        branch=branch
    )

    logger.info(f"✅ '{file_path}' updated with new job IDs.")
