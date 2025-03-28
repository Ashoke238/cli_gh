import unittest
from unittest.mock import patch, MagicMock
from cli.handlers import databricks_handler
from test.test_data import VALID_REPO_NAME
import logging

log_file_path = "test/test_databricks_handler_output.log"
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="w"
)
logger = logging.getLogger(__name__)

class TestDatabricksHandler(unittest.TestCase):

    def log_result(self, test_name, inputs, expected, result, passed=True):
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"--- {status}: {test_name} ---")
        logger.info(f"📥 Inputs: {inputs}")
        logger.info(f"🎯 Expected: {expected}")
        logger.info(f"📤 Actual: {result}")
        logger.info("")

    @patch("cli.handlers.databricks_handler.requests.post")
    def test_import_repo_to_databricks_success(self, mock_post):
        test_name = "Import Repo to Databricks"
        inputs = ("https://github.com/user/myrepo.git", VALID_REPO_NAME)

        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"status": "ok"}

        try:
            databricks_handler.import_repo_to_databricks(*inputs)
            self.log_result(test_name, inputs, "Import successful", "Import successful")
        except Exception as e:
            self.log_result(test_name, inputs, "Import successful", str(e), passed=False)
            self.fail("Unexpected Exception")

    @patch("cli.handlers.databricks_handler.requests.post")
    def test_create_jobs_success(self, mock_post):
        test_name = "Create Databricks Jobs"
        inputs = (VALID_REPO_NAME, "https://github.com/user/myrepo.git")

        # Mock responses for two job creation calls
        mock_post.side_effect = [
            MagicMock(status_code=200, json=lambda: {"job_id": 1234}),
            MagicMock(status_code=200, json=lambda: {"job_id": 5678})
        ]

        try:
            train_id, infer_id = databricks_handler.create_jobs(*inputs)
            self.assertEqual(train_id, 1234)
            self.assertEqual(infer_id, 5678)
            self.log_result(test_name, inputs, "Job IDs returned", f"{train_id}, {infer_id}")
        except Exception as e:
            self.log_result(test_name, inputs, "Job IDs returned", str(e), passed=False)
            self.fail("Unexpected Exception")

    @patch("cli.handlers.databricks_handler.requests.post")
    def test_create_jobs_failure(self, mock_post):
        test_name = "Create Jobs Failure"
        inputs = (VALID_REPO_NAME, "https://github.com/user/myrepo.git")

        mock_post.return_value.status_code = 400
        mock_post.return_value.text = "Bad Request"

        with self.assertRaises(Exception) as context:
            databricks_handler.create_jobs(*inputs)

        self.log_result(test_name, inputs, "Raise Exception", str(context.exception))


if __name__ == "__main__":
    print(f"📜 Running databricks_handler tests... Logs saved to {log_file_path}")
    unittest.main()
