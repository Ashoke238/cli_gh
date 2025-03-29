# CLI\_GH - Automated MLOps Project Setup with Databricks and GitHub

## 🔎 Overview

`cli_gh` is a Python-based CLI tool that fully automates the setup of a Databricks MLOps pipeline. It creates a GitHub repository, uploads notebook templates, sets up secrets, imports code to Databricks, creates training and inference jobs, updates configuration files, and validates the setup end-to-end with a detailed HTML report.

This solution is triggered via GitHub Actions and adheres to modern CI/CD practices.

---

## ⚡ Features

- CLI-driven repository and job creation
- GitHub Actions integration
- Notebooks for training and inference
- Auto-generated configuration updates
- E2E functional validation with GitHub Pages report
- Object-oriented code design
- Extensible, maintainable structure

---

## ⚙️ Pre-requisites

Before running the CLI tool, ensure the following **GitHub repository secrets** are configured:

| Secret Name           | Description                                                                                               |
| --------------------- | --------------------------------------------------------------------------------------------------------- |
| `GH_TOKEN`            | GitHub personal access token with repo access                                                             |
| `DATABRICKS_HOST`     | Databricks workspace host URL (e.g. [https://abc.cloud.databricks.com](https://abc.cloud.databricks.com)) |
| `DATABRICKS_TOKEN`    | Databricks PAT token                                                                                      |
| `DATABRICKS_USERNAME` | Email used in Databricks                                                                                  |
| `MLFLOW_USER_EMAIL`   | MLflow user email (same as `DATABRICKS_USERNAME`)                                                         |

---

## 🔧 Installation

```bash
git clone https://github.com/Ashoke238/cli_gh.git
cd cli_gh
python -m venv venv
source venv/bin/activate  # Use `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

---

## 🚀 Usage

### ὒ7 From Command Line

```bash
python cli/main.py --repo-name test_mlops_01 --accuracy-train 0.85 --accuracy-inference 0.80
```

### ⚖️ From GitHub Actions

Trigger the pipeline manually via **Actions > Run Workflow**, or configure it with:

```yaml
name: Run CLI for Repo Automation
on:
  workflow_dispatch:
    inputs:
      repo_name:
        description: 'Repository Name'
        required: true
      accuracy_train:
        required: true
        default: '0.85'
      accuracy_inference:
        required: true
        default: '0.80'
```

---

## 🌐 Output Artifacts

### ✏️ GitHub Repository Created

- Template notebooks auto-uploaded
- `mlops_config/mlops_config_dev.json` updated with job IDs
- Branch `dev` created

### 💡 Databricks Jobs

- **Train Job**: runs every 30 days
- **Inference Job**: runs every hour

### 📄 E2E HTML Report

- Auto-generated to `/e2e/reports/e2e_report_<repo_name>.html`
- Publishes summary to GitHub Pages: [https://ashoke238.github.io/e2e\_reports](https://ashoke238.github.io/e2e_reports)

---

## 🔍 Validation

Run the validation script to confirm all resources:

```bash
python e2e/run_e2e.py <repo_name>
```

You will find the rendered result under `e2e/reports/`.

---

## 🔹 Folder Structure

```
cli_gh/
├── cli/
│   ├── main.py
│   ├── logger.py
│   ├── validator.py
│   └── handlers/
│       ├── git_handler.py
│       └── databricks_handler.py
├── e2e/
│   ├── e2e_validator.py
│   └── run_e2e.py
├── test/
│   └── test_*.py
├── requirements.txt
└── .github/workflows/cli.yml
```

---

## 📊 Reporting

The final validation report will include:

- Job names, schedules, Git source
- GitHub repo setup status
- Config file update status
- CLI automation health check
- Direct link to Databricks jobs

Example GitHub Pages Report: [View Report](https://ashoke238.github.io/e2e_reports)

---

## 🚀 Future Enhancements

- Automatic model promotion to staging/prod
- Slack/Email notifications
- Integration with MLflow registry APIs
- Multi-environment support (dev, test, prod)

---

## ✉️ Feedback

Please raise issues or suggestions via GitHub Issues.

> Happy Automating 🚀

