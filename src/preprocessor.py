"""
Preprocessor module for Automated Marking System

Provides functions and classes to:
- Execute unit tests within the appropriate task context for student submissions.
- Prepare student submission directories by copying instructor's template test files and scenario variants.
"""
import shutil
from pathlib import Path
from config import TASK_CONFIG
from tqdm import tqdm
    
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

    # Main method to process all student submissions: inject test files, move originals, and apply task-specific overrides
    def process_all_submissions(self) -> None:
        # Step 1: Inject test files into each Portfolio_* submission
        portfolio_submissions = [submission_dir for submission_dir in self.submissions_root.iterdir() 
                                if submission_dir.is_dir() and submission_dir.name.startswith('Portfolio')]
        
        with tqdm(total=len(portfolio_submissions), desc="Injecting test files") as pbar:
            for submission_dir in portfolio_submissions:
                    self._copy_test_files(submission_dir)
                    pbar.update(1)

        # Step 2: Move all original Portfolio_* into Original_Submissions
        self.original_dir.mkdir(exist_ok=True)
        with tqdm(total=len(portfolio_submissions), desc="Moving original submissions") as pbar:
            for submission_dir in portfolio_submissions:
                    shutil.move(str(submission_dir), self.original_dir / submission_dir.name)
                    pbar.update(1)
        
        # Step 3: Create copies and apply overrides
        with tqdm(total=len(self.override_dirs), desc= "Copying and applying overrides") as pbar:
            for version_name, override_files in self.override_dirs.items():
                version_dir = self.submissions_root / version_name
                if version_dir.exists():
                    shutil.rmtree(version_dir)
                shutil.copytree(self.original_dir, version_dir, ignore=shutil.ignore_patterns('venv', '__pycache__'))

                # Apply overrides in each copied submission
                for submission_dir in version_dir.iterdir():
                    if submission_dir.is_dir():
                        self._apply_overrides(submission_dir, override_files)
                pbar.update(1)

    # Copies standard test files (Testing_*.py, Dummy.py, Helper.py) into a student's submission directory
    def _copy_test_files(self, dest_dir: Path) -> None:
        for test_file in self.teacher_test_dir.glob('Testing_*.py'):
            shutil.copy2(test_file, dest_dir / test_file.name)
        for helper_file in ['Dummy.py', 'Helper.py']:
            helper_path = self.teacher_test_dir / helper_file
            if helper_path.exists():
                shutil.copy2(helper_path, dest_dir / helper_file)
            else:
                print(f"Warning: Helper file {helper_file} not found.")

    # Applies override files (e.g., modified task scripts) into a specific student submission directory
    def _apply_overrides(self, submission_dir: Path, override_files: list) -> None:
        for file_name in override_files:
            teacher_file = self.teacher_test_dir / file_name
            if teacher_file.exists():
                shutil.copy2(teacher_file, submission_dir / file_name)
            else:
                print(f"Warning: Teacher override file {file_name} not found.")


if __name__ == "__main__":
    pass
