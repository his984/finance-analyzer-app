# Professional Python Project Setup Guide

This document outlines the standard steps to set up a professional, clean, and automated development environment for a Python project using Visual Studio Code.

---

## Step 1: Isolate Your Project with a Virtual Environment

**Why is this important?** A virtual environment creates an isolated "sandbox" for your project. All the libraries (`pandas`, `customtkinter`, etc.) you install will live inside this sandbox, preventing conflicts with other projects on your computer that might need different versions of the same library. This is the #1 best practice for all Python projects.

### 1.1. Create the Environment
Navigate to your main project folder in the terminal (e.g., `finance-analyzer-app`) and run the following command. This tells Python to create a virtual environment in a folder named `.venv`.

```bash
python -m venv .venv
```

### 1.2. Activate the Environment
You must "activate" the environment for your current terminal session. The command is different for different terminals.

**For PowerShell (in VS Code):**
```powershell
.\.venv\Scripts\Activate.ps1
```
> **Troubleshooting:** If you get a red error message about "execution policies", run this command first to allow scripts for the current session, then try activating again:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`

After successful activation, you will see `(.venv)` at the beginning of your terminal prompt, indicating that the isolated environment is active.

### 1.3. Link VS Code to the Environment
You need to tell VS Code to use the Python interpreter from your new environment.
1.  Press `Ctrl` + `Shift` + `P` to open the Command Palette.
2.  Type and select **"Python: Select Interpreter"**.
3.  Choose the Python interpreter from the list that includes `.venv` in its path. It will be marked with a small folder icon and recommended by VS Code.

---

## Step 2: Manage Dependencies

Now that your environment is active, you can install your project's libraries and lock their versions for reproducibility.

### 2.1. Install Project Libraries
Install all necessary packages inside the **active** virtual environment.

```bash
pip install pandas openpyxl customtkinter CTkTable CTkMessagebox black flake8
```

### 2.2. Create a `requirements.txt` file
This file keeps a record of all the libraries and their specific versions used in your project. This allows any other developer (or you, on a different computer) to replicate your setup perfectly.

```bash
pip freeze > requirements.txt
```
This command automatically generates the file for you. You should commit this file to your Git repository.

---

## Step 3: Configure VS Code for Automated Quality Control

This setup will automatically check and clean your code, saving you time and preventing errors.

### 3.1. Install Required VS Code Extensions
Go to the Extensions view (`Ctrl` + `Shift` + `X`) and make sure you have the following installed:
-   **Python** (ID: `ms-python.python`) - The official extension from Microsoft.
-   **Black Formatter** (ID: `ms-python.black-formatter`) - For automatic code formatting.

### 3.2. Configure `settings.json`
Open your User Settings file (`Ctrl` + `Shift` + `P` -> "Preferences: Open User Settings (JSON)") and ensure the following settings are present. This configuration enables linting with `flake8` and automatic formatting with `black` whenever you save a Python file.

```json
{
    // ... your other settings ...

    // --- Settings for Python Formatting & Linting ---
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.pylintEnabled": false, // Disable the default linter to avoid duplicate messages

    "[python]": {
        "editor.defaultFormatter": "ms-python.black-formatter",
        "editor.formatOnSave": true
    }
}
```

---

## Summary

With these steps completed, any new Python project you start will have:
-   **Isolation:** A dedicated virtual environment to prevent dependency conflicts.
-   **Reproducibility:** A `requirements.txt` file to perfectly recreate the setup.
-   **Quality:** An active linter (`flake8`) to catch errors as you type.
-   **Consistency:** An automatic formatter (`black`) to keep your code clean and readable.

This professional setup is the foundation for building high-quality, maintainable software.