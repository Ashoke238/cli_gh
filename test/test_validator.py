import unittest
import logging
from cli.validator import validate_inputs
from test.test_data import (
    VALID_REPO_NAME, VALID_TRAIN_ACC, VALID_INFER_ACC,
    EMPTY_REPO_NAME, INVALID_REPO_NAME_KEYWORD, INVALID_REPO_NAME_SPECIAL,
    INVALID_TRAIN_ACC, INVALID_INFER_ACC
)

# Configure detailed logging to a file
log_file_path = "test/test_validator_output.log"
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="w"  # Overwrite each time
)
logger = logging.getLogger(__name__)


class TestValidator(unittest.TestCase):

    def log_result(self, test_name, inputs, expected, result, passed=True):
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.info(f"--- {status}: {test_name} ---")
        logger.info(f"📥 Inputs: {inputs}")
        logger.info(f"🎯 Expected: {expected}")
        logger.info(f"📤 Actual: {result}")
        logger.info("")

    def test_empty_repo_name(self):
        test_name = "Empty Repo Name"
        inputs = (EMPTY_REPO_NAME, VALID_TRAIN_ACC, VALID_INFER_ACC)
        expected = "Raise ValueError"
        try:
            validate_inputs(*inputs)
            self.log_result(test_name, inputs, expected, "No Exception", passed=False)
            self.fail("Expected ValueError was not raised.")
        except ValueError as e:
            self.log_result(test_name, inputs, expected, str(e))

    def test_repo_name_with_reserved_keyword(self):
        test_name = "Repo Name with Reserved Keyword"
        inputs = (INVALID_REPO_NAME_KEYWORD, VALID_TRAIN_ACC, VALID_INFER_ACC)
        expected = "Raise ValueError"
        try:
            validate_inputs(*inputs)
            self.log_result(test_name, inputs, expected, "No Exception", passed=False)
            self.fail("Expected ValueError was not raised.")
        except ValueError as e:
            self.log_result(test_name, inputs, expected, str(e))

    def test_repo_name_with_special_chars(self):
        test_name = "Repo Name with Special Characters"
        inputs = (INVALID_REPO_NAME_SPECIAL, VALID_TRAIN_ACC, VALID_INFER_ACC)
        expected = "Raise ValueError"
        try:
            validate_inputs(*inputs)
            self.log_result(test_name, inputs, expected, "No Exception", passed=False)
            self.fail("Expected ValueError was not raised.")
        except ValueError as e:
            self.log_result(test_name, inputs, expected, str(e))

    def test_invalid_training_accuracy(self):
        test_name = "Invalid Training Accuracy"
        inputs = (VALID_REPO_NAME, INVALID_TRAIN_ACC, VALID_INFER_ACC)
        expected = "Raise ValueError"
        try:
            validate_inputs(*inputs)
            self.log_result(test_name, inputs, expected, "No Exception", passed=False)
            self.fail("Expected ValueError was not raised.")
        except ValueError as e:
            self.log_result(test_name, inputs, expected, str(e))

    def test_invalid_inference_accuracy(self):
        test_name = "Invalid Inference Accuracy"
        inputs = (VALID_REPO_NAME, VALID_TRAIN_ACC, INVALID_INFER_ACC)
        expected = "Raise ValueError"
        try:
            validate_inputs(*inputs)
            self.log_result(test_name, inputs, expected, "No Exception", passed=False)
            self.fail("Expected ValueError was not raised.")
        except ValueError as e:
            self.log_result(test_name, inputs, expected, str(e))

    def test_valid_inputs(self):
        test_name = "Valid Inputs"
        inputs = (VALID_REPO_NAME, VALID_TRAIN_ACC, VALID_INFER_ACC)
        expected = "No Exception"
        try:
            result = validate_inputs(*inputs)
            self.log_result(test_name, inputs, expected, "No Exception")
            self.assertIsNone(result)
        except Exception as e:
            self.log_result(test_name, inputs, expected, str(e), passed=False)
            self.fail(f"Unexpected exception raised: {e}")


if __name__ == "__main__":
    print(f"📜 Running validator tests... Logs will be saved to {log_file_path}")
    unittest.main()
