# Automated Student Submission Marker

## Overview
This program is designed to automate the workflow of marking student programming submissions for module CM2203. It handles:

1. **Cleaning raw submissions** (Unzipping, renaming, flattening directories and removing unnecessary files)
2. **Setting up isolated Python environments** for each student submission.
3. **Duplicating submissionis and overriding** specific task files if needed.
3. **Running selected tasks** and logging collated results.

## Features
- Supports bulk unzipping and renaming
- Automatically flattens nested folder structures
- Removes unwanted files like `Dummy.py`, `Images` or others
- High-speed creation of per-student virtual environments
- Installs dependencies from each submission's `requirements.txt`
- Duplicates submissions and overrides specific task files
- Fallback support for virtual environment and dependency installation in case of unexpected errors
- Runs selected tasks with multithreading and timeout support
- Shows real-time progress bar
- GUI for easy operation (e.g., selecting folders, click-to-run)
- Operating System compatibility (Linux-based and Windows). *GUI works better on Windows.*

## Setup Instructions
### Prerequisites
 - Python 3.10+
 - Git

### Step 1: Clone the Repository
```
git clone https://github.com/E-Aghbari/Automated-Marking.git
```
### Step 2: Setup Virtual Environment
```
python -m venv venv
```
### Step 3: Activate Virtual Environment
On Windows (Command Prompt)
```
call venv\Scripts\activate
```
On Mac OS X
```
source venv/bin/activate
```

### Step 4: Install Dependencies
```
pip install -r requirements.txt
```

## CLI Usage
```
python automark.py {commands}
```
Available commands:
- `GUI`: Starts the user interface of the program.

- **`clean-subs`**: Unzip and clean students' submissions.
  - `--nonclean-path` – Absolute path to the folder containing non-cleaned submissions.
  - `--path` – Absolute path to the folder containing CSV files, Testing files folder, and Images.

- **`setup-venvs`**: Set up virtual environments for submissions.
  - `--path` – Absolute path to the folder containing cleaned submissions.

- **`copy-override`**: Copy testing files and override tasks.
    - `--template-path` – Absolute path to the folder containing the template of teacher's tests and task files.
  - `--path` – Absolute path to the folder containing cleaned submissions.

- **`run-tests`**: Run unit tests for all students.
  - `--path` – Absolute path to the folder containing cleaned and prepared submissions.
  - `--tasks` – Comma-separated list of tasks to be tested (e.g., `Task_1,Task_2`).

## GUI Usage
The `Help` button provides you with instructions and things to do before running.

**Non-Cleaned Submissions**
  - **1st Entry**: select folder that contains the Images folder, 'testing files' folder and CSV files (testing_data.csv, training_data.csv, etc..). This is where submissions will be after cleaning.
  - **2nd Entry**: select folder that contains the non-cleaned (zipped) submissions. They will be cleaned and moved to the path selected in 1st entry where CSV, Images, etc.. are at.

**Cleaned Submissions**
 - **Prepare Submissions**: This section is responsible of setting up isolated virtual environments and copying/overriding students' submissions.
   * **1st Entry**: select folder that contains the cleaned submissions.
   * **2nd Entry**: select folder that contains teacher's template python tasks (TemplatePythonModel)

 - **Run Tests**: This section is responsible for running tasks from the folder with cleaned submissions that was provided in previous entries.
   * **Checkboxes**: Check boxes of tasks to run.

**Tip**: The shell/CLI used to start GUI can be used to monitor progress of selected operations (progress bar).

## Requirements
 - Python 3.7+
 - ```pip install -r requirements.txt```

## Project Structure
```
Automated-Marking/
├── .gitignore
├── requirements.txt
├── README.md
└── src/
    ├── automarker_gui_support.py     # Back-end widget functioning
    ├── automarker_gui.py     # Graphical User Interface script
    ├── automarker_gui.tcl      # Front-end widgets and window
    ├── automarker.py     # main script
    ├── clean_submission.py       # cleaning script
    ├── config.py     # Configuration file
    ├── report_generate.py      # generating reports
    ├── 
    └── venv_manager.py     # Managing Virtual Environment
```
## Author
Developed by Ebrahim Al Aghbari, Cardiff University
