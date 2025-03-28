#unit test the validator module
import unittest
from unittest.mock import patch
from cli.validator import validate_inputs
from cli.logger import setup_logger
logger = setup_logger()


#unit test the validate_inputs function
class TestValidator(unittest.TestCase):
    #test case for validate_inputs function
    @patch('cli.validator.logger')
    def test_validate_inputs(self, mock_logger):
        #test case for empty repo name
        with self.assertRaises(ValueError) as context:
            validate_inputs("", 0.85, 0.80)
        self.assertTrue("Repository name cannot be empty." in str(context.exception))

        #test case for repo name containing reserved keyword
        with self.assertRaises(ValueError) as context:
            validate_inputs("mlops_repo", 0.85, 0.80)
        self.assertTrue("Repository name 'mlops_repo' cannot contain reserved keyword 'mlops'." in str(context.exception))

        #test case for repo name containing special characters
        with self.assertRaises(ValueError) as context:
            validate_inputs("mlops_repo$", 0.85, 0.80)
        self.assertTrue("Repository name can only contain letters, numbers, underscores (_), and hyphens (-)." in str(context.exception))

        #test case for invalid training accuracy threshold
        with self.assertRaises(ValueError) as context:
            validate_inputs("mlops_repo", 1.85, 0.80)
        self.assertTrue("Training accuracy threshold '1.85' must be between 0 (exclusive) and 1 (inclusive)." in str(context.exception))

        #test case for invalid inference accuracy threshold
        with self.assertRaises(ValueError) as context:
            validate_inputs("mlops_repo", 0.85, 1.80)
        self.assertTrue("Inference accuracy threshold '1.8' must be between 0 (exclusive) and 1 (inclusive)." in str(context.exception))

        #test case for valid inputs
        self.assertIsNone(validate_inputs("mlops_repo", 0.85, 0.80))
