import click
from logger import setup_logger
from validator import validate_inputs
from handlers.git_handler import validate_repo_availability
from handlers.databricks_handler import validate_databricks_job_availability
import os

logger = setup_logger()

@click.command()
@click.option(
    '--repo-name',
    prompt='Repository Name',
    default=lambda: os.environ.get('REPO_NAME', ''),
    help='Enter the new repository name.'
)
@click.option(
    '--accuracy-train',
    prompt='Accuracy Threshold for Training',
    type=float,
    default=lambda: os.environ.get('ACCURACY_TRAIN', ''),
    help='Enter accuracy threshold for training (e.g., 0.85).'
)
@click.option(
    '--accuracy-inference',
    prompt='Accuracy Threshold for Inference',
    type=float,
    default=lambda: os.environ.get('ACCURACY_INFERENCE', ''),
    help='Enter accuracy threshold for inference (e.g., 0.80).'
)

def main(repo_name, accuracy_train, accuracy_inference):
    logger.info("Starting input validation...")

    try:
        validate_inputs(repo_name, accuracy_train, accuracy_inference)
    except ValueError as e:
        logger.error(f"Validation Failed:\n{e}")
        click.echo(f"\nValidation Failed:\n{e}")
        raise click.Abort()
    
    try:
        validate_repo_availability(repo_name)
        validate_databricks_job_availability(repo_name)
    except ValueError as e:
        logger.error(f"Platform-specific validation failed:\n{e}")
        click.echo(f"\nPlatform-specific validation failed:\n{e}")
    raise click.Abort()


    logger.info("All inputs validated successfully!")
    click.echo(f"\n🎉 Inputs are valid:\n - Repo Name: {repo_name}\n - Train Accuracy: {accuracy_train}\n - Inference Accuracy: {accuracy_inference}")






if __name__ == '__main__':
    main()