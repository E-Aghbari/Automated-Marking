"""
Test Manager Module for Automated Marking System

Provides functions and classes to:
- Execute unit tests within the appropriate task context for student submissions.
- Prepare student submission directories by copying instructor's template test files and scenario variants.
"""
import shutil
from pathlib import Path
from venv_manager import VenvManager
from config import TASK_CONFIG

def run_task(task_name: str, submission_path: Path, venv_manager: VenvManager) -> str:
    """
    Executes the appropriate test script for a specific task using a virtual environment manager.

    Args:
        task_name (str): Identifier for the task to run (e.g., "Task_1").
        submission_path (Path): Path to the student's submission folder.
        venv_manager (VenvManager): Instance managing the Python virtual environment.

    Returns:
        str: Output from the unittest execution, if successful.
    """
    # Retrieve task configuration details
    config = TASK_CONFIG.get(task_name)

    # print("Submission path:", submission_path)

    # # Determine the correct test directory based on scenario presence
    # if config["scenario"]:
    #     # If a scenario is specified, use the submission directory name directly
    #     test_dir = submission_path.parent / f"{submission_path.name}"        
    # else:
    #     test_dir = submission_path  # Use the original directory if no scenario

    test_script = submission_path / config["test_script"]

    # print(f'test_dir: {submission_path}')
    # print(f'test_script: {test_script}')

    # If the test script does not exist in the expected location, raise error
    if not test_script.exists():
        raise FileNotFoundError(f"Test script {test_script} not found in {submission_path}")

    # Run the unittest module using the submission's virtual environment
    try:
        return venv_manager.run_python(
            args=["-m", "unittest", test_script.name],
            cwd=submission_path  # Critical for proper imports within the test environment
        )
    except Exception as e:
        # On failure, write the exception details to a crash log file in the test directory
        with open(submission_path / f"TEST_{task_name}.crash", 'w' ) as f:
            f.write(str(e))
    except ImportError:
        with open(submission_path / f"TEST_{task_name}.crash", 'w' ) as f:
            f.write(f"Import Error; student may installed extra packages")

    
class SubmissionPreprocessor:
    """
    Prepares student submissions by:
    - Copying test files into each original submission.
    - Moving all originals into 'Original_Submissions' folder.
    - Creating two copies with specific task overrides.
    """
    def __init__(self, teacher_test_dir: str, submissions_root: str):
        self.teacher_test_dir = Path(teacher_test_dir)
        self.submissions_root = Path(submissions_root)

        # Step 1: Build override_dirs dynamically from TASK_CONFIG
        self.override_dirs = {}
        for task_name, config in TASK_CONFIG.items():
            scenario = config.get('scenario')
            override_files = config.get('override', [])

            if scenario:  # Only if a scenario is defined (not None)
                self.override_dirs[scenario] = override_files

        # Step 2: Main original directory
        self.original_dir = self.submissions_root / 'Original_Submissions'

    def process_all_submissions(self) -> None:
        # Step 1: Inject test files into each Portfolio_* submission
        for submission_dir in self.submissions_root.iterdir():
            if submission_dir.is_dir() and submission_dir.name.startswith('Portfolio'):
                self._copy_test_files(submission_dir)

        # Step 2: Move all original Portfolio_* into Original_Submissions
        self.original_dir.mkdir(exist_ok=True)
        for submission_dir in self.submissions_root.iterdir():
            if submission_dir.is_dir() and submission_dir.name.startswith('Portfolio'):
                shutil.move(str(submission_dir), self.original_dir / submission_dir.name)

        # Step 3: Create copies and apply overrides
        for version_name, override_files in self.override_dirs.items():
            version_dir = self.submissions_root / version_name
            if version_dir.exists():
                shutil.rmtree(version_dir)
            shutil.copytree(self.original_dir, version_dir, ignore=shutil.ignore_patterns('venv', '__pycache__'))

            # Apply overrides in each copied submission
            for submission_dir in version_dir.iterdir():
                if submission_dir.is_dir():
                    self._apply_overrides(submission_dir, override_files)

    def _copy_test_files(self, dest_dir: Path) -> None:
        for test_file in self.teacher_test_dir.glob('Testing_*.py'):
            shutil.copy2(test_file, dest_dir / test_file.name)
        for helper_file in ['Dummy.py', 'Helper.py']:
            helper_path = self.teacher_test_dir / helper_file
            if helper_path.exists():
                shutil.copy2(helper_path, dest_dir / helper_file)
            else:
                print(f"Warning: Helper file {helper_file} not found.")

    def _apply_overrides(self, submission_dir: Path, override_files: list) -> None:
        for file_name in override_files:
            teacher_file = self.teacher_test_dir / file_name
            if teacher_file.exists():
                shutil.copy2(teacher_file, submission_dir / file_name)
                print(f"Overridden {file_name} in {submission_dir.relative_to(self.submissions_root)}")
            else:
                print(f"Warning: Teacher override file {file_name} not found.")
# class SubmissionPreprocessor:
#     """
#     Handles preparation of student submissions by:
#     - Copying instructor's template test scripts.
#     - Creating scenario-specific copies with overridden files for certain tasks.
#     """
#     def __init__(self, teacher_test_dir: str, submissions_root: str):
#         """
#         Initialise the preprocessor with paths to teacher test files and submissions root.

#         Args:
#             teacher_test_dir (str): Directory containing instructor test scripts and overrides.
#             submissions_root (str): Root directory containing all student submissions.
#         """
#         self.teacher_test_dir = Path(teacher_test_dir)
#         self.submissions_root = Path(submissions_root)

#         # Extract scenarios that require overrides from TASK_CONFIG
#         self.scenarios = [
#             {'name':config['scenario'], 'override': config['override']}
#             for config in TASK_CONFIG.values()
#             if config['scenario'] is not None
#         ]

#     def process_all_submissions(self) -> None:
#         """
#         Iterate over all submissions in the root directory and process those that
#         match the expected naming pattern and are not already preprocessed.
#         """
#         for submission_dir in self.submissions_root.iterdir():
#             # Only process directories
#             if not submission_dir.is_dir():
#                 continue

#             submission_name = submission_dir.name
#             # Process submissions starting with 'Portfolio' and not already processed
#             if submission_name.startswith('Portfolio') and not self._is_preprocessed(submission_name):
#                 self.process_single_submission(submission_dir)
                
#     def process_single_submission(self, submission_path: Path) -> None:
#         """
#         Process a single submission directory by copying instructor test files and
#         creating scenario-specific copies with overrides.

#         Args:
#             submission_path (Path): Path to the student's submission directory.
#         """
#         student_name = submission_path.name
#         print(f"\nProcessing submission: {student_name}")

#         # Copy instructor test files to the original submission directory
#         self._copy_test_files(submission_path)
    
#         # For each scenario, create a copy of the submission with overridden files
#         for scenario in self.scenarios:
#             # Scenario directories follow the naming convention: studentname_scenario
#             scenario_path = self.submissions_root / f"{student_name}_{scenario['name']}"
#             self._copy_submission_version(
#                 src=submission_path,  # Base source directory (original)
#                 dest=scenario_path,
#                 override_files=scenario['override']
#             )

#     def _copy_submission_version(self, src: Path, dest: Path, override_files: list) -> None:
#         """
#         Create a copy of a submission directory applying teacher-specified overrides.

#         Args:
#             src (Path): Source directory to copy from.
#             dest (Path): Destination directory to create.
#             override_files (list): List of filenames to override with teacher versions.
#         """
#         # Remove existing destination directory if it exists to avoid conflicts
#         if dest.exists():
#             shutil.rmtree(dest)
            
#         # Copy the entire submission directory excluding virtual environments and cache
#         shutil.copytree(src, dest, ignore=shutil.ignore_patterns('venv', '__pycache__'))
        
#         # Apply teacher file overrides to the copied directory
#         for file_name in override_files:
#             teacher_file = self.teacher_test_dir / file_name
#             if teacher_file.exists():
#                 shutil.copy2(teacher_file, dest / file_name)
#                 print(f"Overridden {file_name} in {dest.name}")
#             else:
#                 print(f"Warning: Teacher file {file_name} not found")

#     def _copy_test_files(self, dest_dir: Path) -> None:
#         """
#         Copy all instructor test scripts and helper files to the student's submission directory.

#         Args:
#             dest_dir (Path): Destination directory to copy test files into.
#         """
#         # Copy all test files matching 'Testing_*.py'
#         for test_file in self.teacher_test_dir.glob('Testing_*.py'):
#             shutil.copy2(test_file, dest_dir / test_file.name)
#             print(f"Copied test file {test_file.name} to {dest_dir.name}")
#         # Always copy Dummy.py and Helper.py as supporting files
#         shutil.copy2(self.teacher_test_dir / 'Dummy.py', dest_dir / 'Dummy.py')
#         shutil.copy2(self.teacher_test_dir / 'Helper.py', dest_dir / 'Helper.py')
    
#     def _is_preprocessed(self, submission_name: str) -> bool:
#         """
#         Check if a submission directory name indicates it has already been processed
#         for any scenario.

#         Args:
#             submission_name (str): Name of the submission directory.

#         Returns:
#             bool: True if already preprocessed, False otherwise.
#         """
#         return any(submission_name.endswith(f"_{scenario['name']}") for scenario in self.scenarios)


if __name__ == "__main__":
    pass
    # sub = SubmissionPreprocessor(r'TemplatePythonModel', Path(r"tests/Cleaned_Test_Files"))
    # print(sub.override_dirs)
    # path = Path(r"D:\Portfolio\Automated-Marking\mock_generator.py")
    # run_task("Task_1", path,VenvManager(path))
    # print(sub.scenarios)
    # sub.process_all_submissions()
    # run_task("Task_1", )


    # sub.process_single_submission(Path(r"tests/Cleaned_Test_Files/Portfolio 2 Upload Zone_c444"))


    # sub.process_all_submissions()
    # sub.process_all_submissions()