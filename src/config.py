"""
Configuration File for Automated Marking System

Defines:
- TASK_CONFIG: Mapping of task identifiers to their test scripts, scenarios, and override files.
- KEEP_FILES: Set of files to retain when cleaning student submissions.
- DEFAULT_DEPENDENCIES: List of required Python packages to be installed in each submission's virtual environment.
"""

# Configuration for each task used in grading
# Each task maps to:
#   - test_script: The Python file used to run unit tests for that task
#   - scenario: Optional test folder to use instead of the default
#   - override: List of student files that should be overridden by instructor-provided versions
TASK_CONFIG = {
    "Task_1": {
        "test_script": "Testing_1.py",
        "scenario": None, # Keep None for original
        "override": []  # No overrides for Task_1
    },
    "Task_2": {
        "test_script": "Testing_2.py",
        "scenario": "Task1_Override",
        "override": ["Task_1.py"]  # Overriding Task_1.py
    },
    "Task_3": {
        "test_script": "Testing_3.py",
        "scenario": "Task1_Task2_Override",
        "override": ["Task_1.py", "Task_2.py"]  # Overriding Task_1.py & Task_2.py
    },
    "Task_4": {
        "test_script": "Testing_4.py",
        "scenario": None,
        "override": []  # No overrides for Task_4
    },
    "Task_5": {
        "test_script": "Testing_5.py",
        "scenario": None, # Keep None for original
        "override": []  # No overrides for Task_5
    }
}

# Files to retain in each cleaned student submission
# All other files and folders will be removed during the cleaning step
KEEP_FILES = {

            "Task_1.py", 
            "Task_2.py", 
            "Task_3.py", 
            "Task_4.py", 
            "Task_5.py", 
            "requirements.txt", 
            "README.txt", 
            "Helper.py", 
            "notes.txt"
        }

# Required packages to install in each student's virtual environment
# Ensure these match the versions expected by the test scripts
DEFAULT_DEPENDENCIES = [
                "numpy==2.2.2",
                "opencv-python==4.11.0.86",
                "sewar==0.4.6",
                "pillow==11.1.0"
            ]