"""
Automated Marker Main Script

This script provides a command-line interface for automating the process of assessing and grading student programming submissions.
It includes functions for:
  1. Cleaning raw student submissions.
  2. Setting up isolated Python virtual environments for each submission.
  3. Preprocessing student directories by copying submissions and overriding necessary test files.
  4. Running unit tests for selected tasks and generating per-task detailed reports.
  5. Launching a GUI (Graphical User Interface) if needed.

The script uses multithreading for parallel processing and includes progress tracking via tqdm.
"""
from venv_manager import VenvManager
from preprocessor import SubmissionPreprocessor
from config import TASK_CONFIG
from pathlib import Path
from report_generate import generate_detailed_report, generate_setup_report
import argparse
from clean_submission import CleanSubmission
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import os
from tqdm import tqdm
import automarker_gui 

def submission_cleaner(non_cleaned_root: Path, cleaned_path: Path = None) -> Path:
    """
    Cleans raw student submissions by unzipping, renaming, flattening directories, and removing unnecessary files.

    Args:
        non_cleaned_root (Path): Path to the directory containing raw submissions.
        cleaned_path (Path, optional): Path to save cleaned submissions. Defaults to None (Cleaned_Submissions).

    Returns:
        Path: Path to the cleaned submissions directory.
    """
    cl = CleanSubmission(non_cleaned_root, cleaned_path)
    cl.unzip_all()
    cl.flatten_directory()
    cl.remove_unnecessary()
    
    print(f"Cleaned submissions can be found in {cl.cleaned_path}")
    
    return cl.cleaned_path


def setup_virtualenvs(submissions_root: Path) -> None:
    """
    Sets up virtual environments for each cleaned student submission and installs necessary requirements.
    Also generates a setup report.

    Args:
        submissions_root (Path): Path to the directory with cleaned student submissions.
    """
    submissions = [s for s in submissions_root.iterdir() if s.is_dir() and s.name.startswith("Portfolio")]

    def setup(sub):

        v = VenvManager(sub)
        v.create_venv()
        v.install_requirements()
        v.save_log()

    threads = int(os.cpu_count() * 1.5)
    with ThreadPoolExecutor(max_workers=threads) as executor:  
        futures = {executor.submit(setup, sub): sub.name for sub in submissions}

        # Create progress bar
        for future in tqdm(as_completed(futures), total=len(futures), desc="Setting up venvs", unit="student"):
            student_name = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"Error processing {student_name}: {e}")

    generate_setup_report(submissions_root)


def preprocess_subs(teacher_files: Path, submissions_root: Path) -> None:
    """
    Copies student submissions, test files and overrides tasks for each student submission.

    Args:
        teacher_files (Path): Path to the directory containing test templates.
        submissions_root (Path): Path to the directory with cleaned student submissions.
    """

    pre = SubmissionPreprocessor(teacher_files, submissions_root)
    pre.process_all_submissions()


def grade_all_submissions(tasks: list, submissions_root: Path) -> None:
    """
    Grades all student submissions across multiple tasks in parallel and generates reports.

    Args:
        tasks (list): List of task names to be tested.
        submissions_root (Path): Path to the directory with prepared student submissions.
    """
    threads = os.cpu_count() * 1.5

    for task in tasks:
        config = TASK_CONFIG.get(task)
        if not config:
            print(f"Warning: Task '{task}' not found in TASK_CONFIG. Skipping...")
            continue

        if config['scenario']:
            scenario_root = submissions_root / config['scenario']
        else:
            scenario_root = submissions_root / 'Original_Submissions'

        submissions = [
            submission for submission in scenario_root.iterdir()
            if submission.is_dir() and submission.name.startswith("Portfolio")
        ]

        print(f"Grading {len(submissions)} submissions for {task}...")

        with ThreadPoolExecutor(max_workers=threads) as executor:
            future_to_submission = {
                executor.submit(grade_single_submission, task, submission): submission
                for submission in submissions
            }

            with tqdm(total=len(future_to_submission), desc=f"Grading {task}", unit="Submission") as pbar:
                for future in as_completed(future_to_submission):
                    submission = future_to_submission[future]
                    try:
                        future.result()
                    except Exception as e:
                        print(f"Error in {submission.name} for {task}: {e}")
                    pbar.update(1)

        generate_detailed_report(task, scenario_root)


def grade_single_submission(task: str, submission: Path) -> None:
    """
    Grades a single student submission for a specific task.

    Args:
        task (str): Name of the task to grade.
        student_dir (Path): Path to the student's submission directory.
    """

    run_task(task, submission, VenvManager(submission))


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

    test_script = submission_path / config["test_script"]

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


def main():
    """
    Entry point for the CLI tool. Parses command-line arguments and dispatches commands
    to corresponding functions based on user input.
    """
    parser = argparse.ArgumentParser(prog="Automatic Marking",description="Student Submission Automation Tool")
    subparser = parser.add_subparsers(
        dest="command",
        title="Available Commands",
        description="Run a specific step in the marking pipeline",
        required=True
    )

    subparser.add_parser("GUI", help="User interface of the program.")
    
    clean_submissions = subparser.add_parser("clean-subs", help="Unzip and clean students' submissions.")
    clean_submissions.add_argument("--nonclean-path", required=True, help="Absolute path to the folder containing non-cleaned submissions.")
    clean_submissions.add_argument("--path", required=True, help="Absolute path to the folder containing CSV files, 'Testing files' folder and Images")

    setup_venvs = subparser.add_parser("setup-venvs", help="Set up virtual environments for submissions.")
    setup_venvs.add_argument("--path", required=True, help="Absolute path to the folder containing cleaned submissions.")

    pre_submissions = subparser.add_parser("copy-override", help="Copy testing files and override tasks.")
    pre_submissions.add_argument("--template-path", required=True, help="Absolute path to the folder containing the template of teacher's tests and tasks files.")
    pre_submissions.add_argument("--path", required=True, help="Absolute path to the folder containing cleaned submissions.")

    run_tests = subparser.add_parser("run-tests", help="Run unit tests for all students.")
    run_tests.add_argument("--path", required=True, help="Absolute path to the folder containing cleaned and prepared submissions.")
    run_tests.add_argument("--tasks", required=True, help="Type the tasks that need to be tested  separated by a comma (no spacing). E.g: Task_1,Task_2")

    args = parser.parse_args()

    if args.command == "GUI":
        automarker_gui.start_up()
        return
    
    path = Path(args.path)

    if args.command == "clean-subs":
        nonClean = Path(args.nonclean_path)
        submission_cleaner(nonClean, path)

    elif args.command == "copy-override":
        test_path = Path(args.template_path)
        preprocess_subs(test_path, path)

    elif args.command == "setup-venvs":
        setup_virtualenvs(path)

    elif args.command == "run-tests":
        tasks = (args.tasks).split(',')
        grade_all_submissions(tasks, path)
        
    
if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Missing command.\n")
        print("Usage: python3 main.py {clean-submissions,prep-submissions,setup-venvs,run-tests}")
        print("Use `-h` or `--help` after a command for more info.")
        print()
        sys.exit(1)

    main()