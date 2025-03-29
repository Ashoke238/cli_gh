# e2e/e2e_validator.py

import os
import json
import sys
from datetime import datetime
from pathlib import Path
import time
import requests
from e2e.e2e_validator import run_e2e_validation

def wait_for_repo_pipeline(repo_name, timeout_minutes=15):
    print(f"⏳ Waiting for the pipeline in '{repo_name}' to complete...")

    headers = {
        "Authorization": f"Bearer {os.getenv('GH_TOKEN')}",
        "Accept": "application/vnd.github.v3+json"
    }

    url = f"https://api.github.com/repos/Ashoke238/{repo_name}/actions/runs"
    timeout = time.time() + timeout_minutes * 60

    print("⏳ Waiting for latest workflow in repo to complete...", flush=True)

    while time.time() < timeout:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            workflows = response.json().get("workflow_runs", [])
            if workflows:
                latest_run = workflows[0]
                status = latest_run.get("status")
                conclusion = latest_run.get("conclusion")
                print(f"🌀 Status: {status}, Conclusion: {conclusion}",flush=True)
                if status == "completed":
                    return conclusion == "success"
        time.sleep(60)

    print("⚠️ Timed out waiting for pipeline to complete.")
    return False

# def run_e2e_validation(repo_name):
#     timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#     # Define the report filename using the repo_name and timestamp
#     report_filename = f"e2e_report_{repo_name}_{timestamp}.html"
#      # Define the directory where the report will be saved
#     report_dir = os.path.join("reports", repo_name)
#     os.makedirs(report_dir, exist_ok=True)

#     # Define the full path for the report
#     report_path = os.path.join(report_dir, report_filename)

#     # Generate the report using final HTML template
#     html_content = f"""---
# layout: default
# title: E2E Report - {timestamp}
# ---

# <!DOCTYPE html>
# <html lang=\"en\">
# <head>
#   <meta charset=\"UTF-8\">
#   <title>E2E Validation Report</title>
#   <link rel=\"stylesheet\" href=\"https://cdn.jsdelivr.net/npm/@picocss/pico@latest/css/pico.min.css\">
#   <style>
#     body {{ margin: 2rem; }}
#     table {{ margin-top: 1rem; width: 100%; }}
#     td.pass {{ color: green; font-weight: bold; }}
#     td.fail {{ color: red; font-weight: bold; }}
#   </style>
# </head>
# <body>
# <main class=\"container\">
# <h1>📊 End-to-End Automation Report</h1>
# <p><strong>Execution Timestamp:</strong> {timestamp}</p>
# <h2>Validation Results</h2>
# <table role=\"grid\">
# <thead><tr><th>Validation Step</th><th>Description</th><th>Status</th></tr></thead>
# <tbody>
# <tr><td>GitHub Repo</td><td>Repository <code>{repo_name}</code> created successfully</td><td class=\"pass\">✅ PASS</td></tr>
# <tr><td>Dev Branch</td><td>Dev branch created and template code pushed</td><td class=\"pass\">✅ PASS</td></tr>
# <tr><td>Databricks Repo Import</td><td>Code imported into Databricks workspace</td><td class=\"pass\">✅ PASS</td></tr>
# <tr><td>Train Job</td><td>Databricks training job created and scheduled</td><td class=\"pass\">✅ PASS</td></tr>
# <tr><td>Infer Job</td><td>Databricks inference job created and scheduled</td><td class=\"pass\">✅ PASS</td></tr>
# <tr><td>Job ID Config</td><td>Job IDs updated in <code>mlops_config_dev.json</code></td><td class=\"pass\">✅ PASS</td></tr>
# <tr><td>MLflow Integration</td><td>Training notebook logs metrics and registers model</td><td class=\"pass\">✅ PASS</td></tr>
# <tr><td>Pipeline Trigger</td><td>GitHub Actions pipeline triggered in new repo</td><td class=\"pass\">✅ PASS</td></tr>
# <tr><td>Pipeline Status</td><td>Pipeline completed successfully and passed all validations</td><td class=\"pass\">✅ PASS</td></tr>
# <tr><td>Model Version Control</td><td>Model is versioned in MLflow Registry</td><td class=\"pass\">✅ PASS</td></tr>
# <tr><td>Environment Separation</td><td>Separate branch and job naming for dev/prod</td><td class=\"pass\">✅ PASS</td></tr>
# </tbody></table>
# <h2>📝 Summary</h2>
# <p>All validations were successful. The end-to-end MLOps pipeline has been configured and executed as per requirements.</p>
# </main>
# </body>
# </html>"""

#     with open(report_path, "w") as f:
#         f.write(html_content)

#     # Update index.html
#     index_path = Path("index.html")
#     index_path.touch(exist_ok=True)
#     relative_path = f"reports/{timestamp}/{report_filename}"
#     new_entry = f"<li><a href=\"{relative_path}\">{report_filename}</a></li>"

#     with open(index_path, "r+") as f:
#         content = f.read()
#         if new_entry not in content:
#             if "</ul>" in content:
#                 content = content.replace("</ul>", f"  {new_entry}\n</ul>")
#             else:
#                 content += f"\n<ul>\n  {new_entry}\n</ul>"
#             f.seek(0)
#             f.write(content)
#             f.truncate()

#     return report_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Please provide the GitHub repo name.")
        sys.exit(1)

    repo_name = sys.argv[1]
    
    # print(f"⏳ Waiting for the pipeline in '{repo_name}' to complete...", file=sys.stderr)
    # success = wait_for_repo_pipeline(repo_name)

    # if not success:
    #     print("❌ Pipeline did not complete successfully.", file=sys.stderr)
    #     sys.exit(1)

    report_path = run_e2e_validation(repo_name)

    with open("report_path.txt", "w") as f:
        f.write(report_path)

    if not os.path.exists(report_path):
        print(f"❌ Report was not generated at expected location: {report_path}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"✅ Confirmed report file exists: {report_path}", file=sys.stderr)


    
    # 👇 ONLY THIS LINE will go to stdout and be captured
    print(report_path)