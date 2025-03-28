import unittest
from unittest.mock import patch, MagicMock
from cli.handlers import git_handler
from test.test_data import VALID_REPO_NAME
import logging
from github.GithubException import GithubException

# Set up test logger
log_file_path = "test/test_git_handler_output.log"
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="w"
)
logger = logging.getLogger(__name__)

class TestGitHandler(unittest.TestCase):

    def log_result(self, test_name, inputs, expected, result, passed=True):
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"--- {status}: {test_name} ---")
        logger.info(f"📥 Inputs: {inputs}")
        logger.info(f"🎯 Expected: {expected}")
        logger.info(f"📤 Actual: {result}")
        logger.info("")

    @patch("cli.handlers.git_handler.Github")
    def test_validate_repo_availability_when_available(self, mock_github):
        test_name = "Validate Repo Availability - Available"
        inputs = (VALID_REPO_NAME,)
        mock_user = MagicMock()
        mock_404_exception = GithubException(404, {"message": "Not Found"}, None)
        mock_user.get_repo.side_effect = mock_404_exception
        mock_github.return_value.get_user.return_value = mock_user

        try:
            git_handler.validate_repo_availability(VALID_REPO_NAME)
            self.log_result(test_name, inputs, "Pass silently", "Pass silently")
        except Exception as e:
            self.log_result(test_name, inputs, "Pass silently", str(e), passed=False)
            self.fail(f"Unexpected Exception: {e}")

    @patch("cli.handlers.git_handler.Github")
    def test_create_github_repo(self, mock_github):
        test_name = "Create GitHub Repo"
        inputs = (VALID_REPO_NAME,)
        mock_repo = MagicMock()
        mock_github.return_value.get_user.return_value.create_repo.return_value = mock_repo

        try:
            result = git_handler.create_github_repo(VALID_REPO_NAME)
            self.assertEqual(result, mock_repo)
            self.log_result(test_name, inputs, "Repo object", "Repo object")
        except Exception as e:
            self.log_result(test_name, inputs, "Repo object", str(e), passed=False)
            self.fail(f"Unexpected exception: {e}")

    @patch("cli.handlers.git_handler.requests.get")
    @patch("cli.handlers.git_handler.zipfile.ZipFile")
    def test_download_and_extract_template(self, mock_zipfile, mock_requests):
        test_name = "Download and Extract Template"
        inputs = ()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'dummy zip'
        mock_requests.return_value = mock_response

        mock_zip_context = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_context

        # simulate directory creation
        with patch("cli.handlers.git_handler.os.listdir") as mock_listdir:
            mock_listdir.return_value = ["model_train_infer-main"]
            with patch("cli.handlers.git_handler.os.path.isdir", return_value=True):
                result = git_handler.download_and_extract_template()
                self.assertTrue(result.endswith("model_train_infer-main"))
                self.log_result(test_name, inputs, "Extracted folder path", result)

    @patch("cli.handlers.git_handler.Github")
    def test_create_dev_branch(self, mock_github):
        test_name = "Create Dev Branch"
        inputs = (VALID_REPO_NAME,)
        mock_repo = MagicMock()
        mock_repo.get_git_ref.return_value.object.sha = "dummy_sha"
        mock_user = MagicMock()
        mock_user.get_repo.return_value = mock_repo
        mock_github.return_value.get_user.return_value = mock_user

        try:
            git_handler.create_dev_branch(VALID_REPO_NAME)
            self.log_result(test_name, inputs, "Dev branch created", "Dev branch created")
        except Exception as e:
            self.log_result(test_name, inputs, "Dev branch created", str(e), passed=False)
            self.fail(f"Failed to create branch: {e}")

if __name__ == "__main__":
    print(f"📜 Running git_handler tests... Logs will be saved to {log_file_path}")
    unittest.main()
