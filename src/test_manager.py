from contextlib import contextmanager
import shutil
import os
from pathlib import Path
from venv_manager import VenvManager


TASK_CONFIG = {
    "Task_1": {
        "test_script": "Testing_1.py",
        "scenario": None
    },
    "Task_2": {
        "test_script": "Testing_2.py",
        "scenario": "Task1_Override"
    },
    "Task_3": {
        "test_script": "Testing_3.py",
        "scenario": "Task1_Task2_Override"
    },
    "Task_4": {
        "test_script": "Testing_4.py",
        "scenario": None
    },
    "Task_5": {
        "test_script": "Testing_5.py",
        "scenario": None
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
    
# def submission_manager(submission_name: str, scenario: str):
#     if submission_name.endswith("Override"):
#         original_name = submission_name.replace(f"_{scenario["scenario"]}", "")
#         return original_name
    

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
        for submission_dir in self.submissions_root.iterdir():
            if not submission_dir.is_dir():
                continue

            submission_name = submission_dir.name
            if submission_name.startswith('Portfolio')and not self._is_preprocessed(submission_name) :
                self.process_single_submission(submission_dir)
                
    def process_single_submission(self, submission_path: Path):

        student_name = submission_path.name
        print(f"\nProcessing submission: {student_name}")

        # Copy test files to the "Original" directory
        self._copy_test_files(submission_path)
    
        # Create scenario copies using the "Original" directory as the source
        for scenario in self.scenarios:
            scenario_path = self.submissions_root / f"{student_name}_{scenario['name']}"
            self._copy_submission_version(
                src=submission_path,  # Use "Original" as the base
                dest=scenario_path,
                override_files=scenario['override']
            )

    def _copy_submission_version(self, src: Path, dest: Path, override_files: list):
        # Remove existing copy if exists
        if dest.exists():
            shutil.rmtree(dest)
            
        # Copy original files
        shutil.copytree(src, dest, ignore=shutil.ignore_patterns('venv', '__pycache__'))
        
        # Apply teacher file overrides
        for file_name in override_files:
            teacher_file = self.teacher_test_dir / file_name
            if teacher_file.exists():
                shutil.copy2(teacher_file, dest / file_name)
                print(f"Overridden {file_name} in {dest.name}")
            else:
                print(f"Warning: Teacher file {file_name} not found")

    def _copy_test_files(self, dest_dir: Path):
        for test_file in self.teacher_test_dir.glob('Testing_*.py'):
            shutil.copy2(test_file, dest_dir / test_file.name)
            print(f"Copied test file {test_file.name} to {dest_dir.name}")
        shutil.copy2(self.teacher_test_dir / 'Dummy.py', dest_dir / 'Dummy.py')
        shutil.copy2(self.teacher_test_dir / 'Helper.py', dest_dir / 'Helper.py')

    def _ignore_temp_dirs(self, path: str, names: list) -> set:
        """Ignore temp directories during copy"""
        return {name for name in names if name in [s['name'] for s in self.scenarios]}
    
    def _is_preprocessed(self, submission_name: str):
        """Check whether submission was processed before"""
        return any(submission_name.endswith(f"_{scenario['name']}") for scenario in self.scenarios)


if __name__ == "__main__":

    sub = SubmissionPreprocessor(r'TemplatePythonModel', Path(r"tests/Cleaned_Test_Files"))
    sub.process_all_submissions()
    # run_task("Task_1", )

    # process_single_submission(Path(r"tests/Cleaned_Test_Files/Portfolio 2 Upload Zone_c000000"))


    # sub.process_all_submissions()
    # sub.process_all_submissions()