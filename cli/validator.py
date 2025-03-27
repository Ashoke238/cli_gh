import re

RESERVED_KEYWORDS = ['train', 'infer', 'dev', 'prod', 'mlops']

def validate_inputs(repo_name, accuracy_train, accuracy_inference):
    errors = []

    # Validate Repo Name
    if not repo_name:
        errors.append("❌ Repository name cannot be empty.")
    else:
        repo_name_lower = repo_name.lower()
        for keyword in RESERVED_KEYWORDS:
            if keyword in repo_name_lower:
                errors.append(
                    f"❌ Repository name '{repo_name}' cannot contain reserved keyword '{keyword}'."
                )
                break  # No need to check further keywords once found

        if not re.match(r'^[a-zA-Z0-9_\-]+$', repo_name):
            errors.append(
                "❌ Repository name can only contain letters, numbers, underscores (_), and hyphens (-)."
            )

    # Validate Training Accuracy Threshold
    if not isinstance(accuracy_train, (float, int)):
        errors.append("❌ Training accuracy threshold must be numeric.")
    elif not (0.0 < float(accuracy_train) <= 1.0):
        errors.append(
            f"❌ Training accuracy threshold '{accuracy_train}' must be between 0 (exclusive) and 1 (inclusive)."
        )

    # Validate Inference Accuracy Threshold
    if not isinstance(accuracy_inference, (float, int)):
        errors.append("❌ Inference accuracy threshold must be numeric.")
    elif not (0.0 < float(accuracy_inference) <= 1.0):
        errors.append(
            f"❌ Inference accuracy threshold '{accuracy_inference}' must be between 0 (exclusive) and 1 (inclusive)."
        )

    # If there are any errors, raise exception summarizing clearly
    if errors:
        error_message = "\n".join(errors)
        raise ValueError(f"Input Validation Errors:\n{error_message}")
