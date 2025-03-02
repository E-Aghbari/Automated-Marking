from contextlib import contextmanager
import shutil
import os
from pathlib import Path
from venv_manager import VenvManager


TASK_CONFIG = {
    "Task_1": {
        "test_script": "Testing_1.py",
        "scenario": None  # Indicates main submission directory
    },
    "Task_2": {
        "test_script": "Testing_2.py",
        "scenario": "Task1_Override"
    },
    "Task_3": {
        "test_script": "Testing_3.py",
        "scenario": "Task1_Task2_Override"
    }
}

"""Create a custom context manager to override files when executing tasks."""
@contextmanager
def overrideFiles(teacherPath, studentPath, tasksToOverride):
    
    ## Create backup directory
    backupPath = os.path.join(studentPath, "backup")
    os.makedirs(backupPath, exist_ok=True)

    ## Track the files that were backed up
    backups= []
    try:
        for task in tasksToOverride:

            ## Prepare task paths
            studentFile = os.path.join(studentPath, task)
            backupFile = os.path.join(backupPath, f"{task}.bak")
            teacherFile = os.path.join(teacherPath, task)

            ## Back up student's task files in case they exist.
            if os.path.exists(studentFile):
                shutil.copy2(studentFile, backupFile)
                backups.append((backupFile, studentFile))
            else:
                print(f"Student {task} does not exist.")

            ## Override student's task file with teacher's version.
            if os.path.exists(teacherFile):
                shutil.copy2(teacherFile, studentFile)
            else:
                print(f"Teacher {task} does not exist.")

        yield
        
    finally:

        ## Restore the original student's task file after executing the test.
        for backup, student in backups:
            if os.path.exists(backupFile):
                shutil.move(backup, student)

def run_task(task_name: str, submission_path: Path, venv_manager: VenvManager):
    """Run test in appropriate directory"""
    config = TASK_CONFIG.get(task_name)
    if not config:
        raise ValueError(f"Unknown task: {task_name}")
    
    # Determine test directory
    if config["scenario"]:
        test_dir = submission_path / config["scenario"]
    else:
        test_dir = submission_path  # Original directory
    
    test_script = test_dir / config["test_script"]
    print(f"Looking for test script: {test_script}")

    if not test_script.exists():
        raise FileNotFoundError(f"Test script {test_script} not found")

    # Run test from the appropriate directory
    return venv_manager.run_python(
        args=["-m", "unittest", test_script.name],
        cwd=test_dir # Critical for proper imports
    )
    

class SubmissionPreprocessor:
    def __init__(self, teacher_test_dir: str, submissions_root: str):
        self.teacher_test_dir = Path(teacher_test_dir)
        self.submissions_root = Path(submissions_root)
        self.scenarios = [
            # {'name': 'Original', 'override': []},
            {'name': 'Task1_Override', 'override': ['Task_1.py']},
            {'name': 'Task1_Task2_Override', 'override': ['Task_1.py', 'Task_2.py']}
        ]

    def process_all_submissions(self):
        """Process all submissions in the root directory"""
        for submission_dir in self.submissions_root.iterdir():
            if submission_dir.is_dir():
                self.process_single_submission(submission_dir)

    def process_single_submission(self, submission_path: Path):
        """Process a single submission directory"""
        print(f"\nProcessing submission: {submission_path.name}")

        # Copy test files to scenario copy
        self._copy_test_files(submission_path)
        
        # Create scenario copies
        for scenario in self.scenarios:
            scenario_path = submission_path / scenario['name']
            self._copy_submission_version(
                src=submission_path,
                dest=scenario_path,
                override_files=scenario['override']
            )

    def _copy_submission_version(self, src: Path, dest: Path, override_files: list):
        """Create a scenario copy with specified file overrides"""
        # Remove existing copy if exists
        if dest.exists():
            shutil.rmtree(dest)
            
        # Copy original files
        shutil.copytree(src, dest, ignore=self._ignore_temp_dirs)
        
        # Apply teacher file overrides
        for file_name in override_files:
            teacher_file = self.teacher_test_dir / file_name
            if teacher_file.exists():
                shutil.copy2(teacher_file, dest / file_name)
                print(f"Overridden {file_name} in {dest.name}")
            else:
                print(f"Warning: Teacher file {file_name} not found")

    def _copy_test_files(self, dest_dir: Path):
        """Copy all test files to target directory"""
        for test_file in self.teacher_test_dir.glob('Testing_*.py'):
            shutil.copy2(test_file, dest_dir / test_file.name)
            print(f"Copied test file {test_file.name} to {dest_dir.name}")
        shutil.copy2(self.teacher_test_dir / 'Dummy.py', dest_dir / 'Dummy.py')

    def _ignore_temp_dirs(self, path: str, names: list) -> set:
        """Ignore temp directories during copy"""
        return {name for name in names if name in [s['name'] for s in self.scenarios]}


if __name__ == "__main__":

    sub = SubmissionPreprocessor("TemplatePythonModel", "tests/Cleaned_Test_Files")

    sub.process_all_submissions()
    # sub.process_all_submissions()