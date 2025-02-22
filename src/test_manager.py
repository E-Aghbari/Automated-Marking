from contextlib import contextmanager
import shutil
import os
from pathlib import Path


TASK_CONFIG = {
    "Task_1": {
        "files_to_override": [],
        "test_script": "tests.TemplatePythonModel.Testing_1.py"
    },
    "Task_2": {
        "files_to_override": ["Task_1.py"],
        "test_script": "Testing_2.py"
    },
    "Task_3": {
        "files_to_override": ["Task_1.py", "Task_2.py"],
        "test_script": "Testing_3.py"
    }
}

"""Create a custom context manager to override files when executing tasks."""
@contextmanager
def overrideFiles(teacherPath, studentPath, taskNames):
    
    ## Create backup directory
    backupPath = os.path.join(studentPath, "backup")
    os.makedirs(backupPath, exist_ok=True)

    ## Track the files that were backed up
    backups= []
    try:
        for task in taskNames:

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

def run_task(taskName, teacherPath, studentPath, venvManager):
    config = TASK_CONFIG[taskName]
    files_to_override = config["files_to_override"]
    test_script = config["test_script"]

    with overrideFiles(teacherPath, studentPath, files_to_override):
       return venvManager.run_python(["-m", "unittest", test_script])
    

class SubmissionPreprocessor:
    def __init__(self, teacher_test_dir: str, submissions_root: str):
        self.teacher_test_dir = Path(teacher_test_dir)
        self.submissions_root = Path(submissions_root)
        self.scenarios = [
            {'name': 'Original', 'override': []},
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
        
        # Create scenario copies
        for scenario in self.scenarios:
            scenario_path = submission_path / scenario['name']
            self._copy_submission_version(
                src=submission_path,
                dest=scenario_path,
                override_files=scenario['override']
            )
            
            # Copy test files to scenario copy
            self._copy_test_files(scenario_path)

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

    def _ignore_temp_dirs(self, path: str, names: list) -> set:
        """Ignore temp directories during copy"""
        return {name for name in names if name in [s['name'] for s in self.scenarios]}
    
sub = SubmissionPreprocessor("TemplatePythonModel", "tests\Cleaned_Test_Files")

sub.process_single_submission(Path("tests\Cleaned_Test_Files\Portfolio 2 Upload Zone_c000000"))