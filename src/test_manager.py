import shutil
from pathlib import Path
from venv_manager import VenvManager
from config import TASK_CONFIG

def run_task(task_name: str, submission_path: Path, venv_manager: VenvManager):
    """Run the test script using the correct test directory."""
    config = TASK_CONFIG.get(task_name)
    if not config:
        raise ValueError(f"Unknown task: {task_name}")

    print("Submission path:", submission_path)

    # Determine the correct test directory
    if config["scenario"]:
        # scenario_suffix = f"_{config['scenario']}"
        # Only append the scenario suffix if it’s not already in the path
        test_dir = submission_path.parent / f"{submission_path.name}"        
    else:
        test_dir = submission_path  # Original directory

    test_script = test_dir / config["test_script"]

    print("Correct test directory:", test_dir)
    print(f"Looking for test script: {test_script}")

    if not test_script.exists():
        raise FileNotFoundError(f"Test script {test_script} not found in {test_dir}")

    # Run test from the appropriate directory
    try:
        return venv_manager.run_python(
            args=["-m", "unittest", test_script.name],
            cwd=test_dir  # Critical for proper imports
        )
    except Exception as e:
        with open(test_dir / f"TEST_{task_name}.crash", 'w' ) as f:
            f.write(str(e))

    

# def run_task(task_name: str, submission_path: Path, venv_manager: VenvManager):
#     config = TASK_CONFIG.get(task_name)
#     if not config:
#         raise ValueError(f"Unknown task: {task_name}")
#     print("submpssion path",submission_path)
    
#     # Determine test directory
#     if config["scenario"]:
#         test_dir = submission_path.parent / f'{submission_path}_{config["scenario"]}'
#     else:
#         test_dir = submission_path  # Original directory
    
#     test_script = test_dir / config["test_script"]

#     print("WHASSJFKSJFL", test_dir)
#     print(f"Looking for test script: {test_script}")

#     if not test_script.exists():
#         raise FileNotFoundError(f"Test script {test_script} not found")

#     # Run test from the appropriate directory
#     return venv_manager.run_python(
#         args=["-m", "unittest", test_script.name],
#         cwd=test_dir # Critical for proper imports
#     )
    

class SubmissionPreprocessor:
    def __init__(self, teacher_test_dir: str, submissions_root: str):
        self.teacher_test_dir = Path(teacher_test_dir)
        self.submissions_root = Path(submissions_root)
        self.scenarios = [
            {'name':config['scenario'], 'override': config['override']}
            for config in TASK_CONFIG.values()
            if config['scenario'] is not None
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
    # print(sub.scenarios)
    sub.process_all_submissions()
    # run_task("Task_1", )

    # sub.process_single_submission(Path(r"tests/Cleaned_Test_Files/Portfolio 2 Upload Zone_c444"))


    # sub.process_all_submissions()
    # sub.process_all_submissions()