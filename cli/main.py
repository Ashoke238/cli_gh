import os
import click
from dotenv import load_dotenv
from logger import setup_logger
from validator import validate_inputs

from handlers.git_handler import (
    validate_repo_availability,
    create_and_setup_repo,
    update_config_json
)
from handlers.databricks_handler import (
    validate_databricks_job_availability,
    import_repo_to_databricks,
    create_jobs
)

# Load environment variables
load_dotenv()

logger = setup_logger()

# Databricks Username from environment
#DATABRICKS_USERNAME = os.getenv("DATABRICKS_USERNAME")

@click.command()
@click.option('--repo-name', prompt='Repository Name', envvar='REPO_NAME', help='Enter your new repository name.')
@click.option('--accuracy-train', prompt='Accuracy Threshold (Training)', type=float, envvar='ACCURACY_TRAIN', help='Enter the accuracy threshold for training (0 to 1).')
@click.option('--accuracy-inference', prompt='Accuracy Threshold (Inference)', type=float, envvar='ACCURACY_INFERENCE', help='Enter the accuracy threshold for inference (0 to 1).')
def main(repo_name, accuracy_train, accuracy_inference):
    try:
        # Step 1: Common Input Validation
        logger.info("✅ Validating input parameters...")
        validate_inputs(repo_name, accuracy_train, accuracy_inference)
        logger.info("✅ Input parameters validated successfully.")

        # Step 2: Platform-specific validation
        logger.info("✅ Checking GitHub repo and Databricks job availability...")
        validate_repo_availability(repo_name)
        validate_databricks_job_availability(repo_name)
        logger.info("✅ GitHub and Databricks validations passed.")

        # Step 3: GitHub Repository Creation, Clone Template, Setup Dev branch
        logger.info("✅ Creating and setting up GitHub repository...")
        git_url = create_and_setup_repo(repo_name)
        logger.info(f"✅ GitHub repository '{repo_name}' set up successfully at {git_url}.")

        # Step 4: Import repository into Databricks
        logger.info("✅ Importing repository into Databricks...")
        import_repo_to_databricks(git_url, repo_name)
        logger.info("✅ GitHub repository imported into Databricks successfully.")

        # Step 5: Create Databricks Jobs (Train & Infer)
        logger.info("✅ Creating Databricks jobs (training & inference)...")
        train_job_id, infer_job_id = create_jobs(repo_name, git_url)
        logger.info(f"✅ Databricks jobs created successfully (Train Job ID: {train_job_id}, Infer Job ID: {infer_job_id}).")

        # Step 6: Update Job IDs in JSON configuration file in GitHub repo
        logger.info("✅ Updating configuration JSON file with Databricks Job IDs...")
        update_config_json(repo_name, train_job_id, infer_job_id)
        logger.info("✅ Configuration JSON file updated and committed successfully.")

        logger.info("🎉 All tasks executed successfully!")
        click.echo("🎉 All tasks executed successfully!")

    except Exception as e:
        logger.error(f"❌ An error occurred", exc_info=True)
        click.echo(f"❌ An error occurred: {str(e)}", err=True)
        raise click.Abort()

if __name__ == '__main__':
    main()
