# run_e2e.py

import sys
from e2e.e2e_validator import run_e2e_validation

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Please provide the GitHub repo name.")
        sys.exit(1)
    repo_name = sys.argv[1]
    report_path = run_e2e_validation(repo_name)
    print(f"✅ Report generated at {report_path}")
