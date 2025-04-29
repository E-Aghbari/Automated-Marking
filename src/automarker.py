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
from test_manager import SubmissionPreprocessor, run_task
from config import TASK_CONFIG
from pathlib import Path
from report_generate import generate_detailed_report, generate_setup_report
import argparse
from clean_submission import CleanSubmission
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import sys
import os
from tqdm import tqdm
import automarker_gui 
import asyncio

def submission_cleaner(non_cleaned_root: Path, cleaned_path: Path = None) -> Path:
    """
    Cleans raw student submissions by unzipping, renaming, flattening directories, and removing unnecessary files.

    Args:
        non_cleaned_root (Path): Path to the directory containing raw submissions.
        cleaned_path (Path, optional): Path to save cleaned submissions. Defaults to None (Cleaned_Submissions).

    Returns:
        Path: Path to the cleaned submissions directory.
    """

    start_time = time.perf_counter()

    cl = CleanSubmission(non_cleaned_root, cleaned_path)
    cl.unzip_all()
    cl.flatten_directory()
    cl.remove_unnecessary()
    
    print(f"Cleaned submissions can be found in {cl.cleaned_path}")
    
    end_time = time.perf_counter()

    duration = end_time - start_time
    # print(f"Finished setting up venvs for 205 students in {duration:.2f} seconds.")

    return cl.cleaned_path


def setup_virtualenvs(submissions_root: Path) -> None:
    """
    Sets up virtual environments for each cleaned student submission and installs necessary requirements.
    Also generates a setup report.

    Args:
        submissions_root (Path): Path to the directory with cleaned student submissions.
    """
    # print_lock = Lock()
    

    start_time = time.perf_counter()
    # prepare_base_venv()

    submissions = [s for s in submissions_root.iterdir() if s.is_dir() and s.name.startswith("Portfolio")]
    # for sub in tqdm(submissions, desc="Setting up Virtual Environments", unit="Submission"):
    #     v = VenvManager(sub)
    #     v.create_venv()
    #     v.install_requirements()
    #     v.save_log()

    def setup(sub):
        # with print_lock:
        #     print(f"Starting setup for {sub.name}")
        v = VenvManager(sub)
        v.create_venv()
        v.install_requirements()
        v.save_log()
        # with print_lock:
        #     print(f"Finished setup for {sub.name}")

    threads = int(os.cpu_count() * 1.5)
    with ThreadPoolExecutor(max_workers=threads) as executor:  # Adjust number of threads based on CPU
        futures = {executor.submit(setup, sub): sub.name for sub in submissions}

        # Create progress bar
        for future in tqdm(as_completed(futures), total=len(futures), desc="Setting up venvs", unit="student"):
            student_name = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"Error processing {student_name}: {e}")

            # student = futures[future]
            # print(f"Finished setup for {student}")
        # list(tqdm(executor.map(setup, submissions), total= len(submissions), desc="Setting up venvs", unit="student"))
        
    generate_setup_report(submissions_root)
    end_time = time.perf_counter()

    duration = end_time - start_time
    print(f"Finished setting up venvs for {len(submissions)} students in {duration:.2f} seconds.")

    # 61.91 secs


def preprocess_subs(teacher_files: Path, submissions_root: Path) -> None:
    """
    Copies student submissions, test files and overrides tasks for each student submission.

    Args:
        teacher_files (Path): Path to the directory containing test templates.
        submissions_root (Path): Path to the directory with cleaned student submissions.
    """

    pre = SubmissionPreprocessor(teacher_files, submissions_root)

    pre.process_all_submissions()

def batch_list(lst, batch_size):
    """Helper to split list into batches."""
    for i in range(0, len(lst), batch_size):
        yield lst[i:i + batch_size]


def grade_all_submissions(tasks: list, submissions_root: Path, batch_size= 10) -> None:
    """
    Grades all student submissions across multiple tasks in parallel and generates reports.

    Args:
        tasks (list): List of task names to be tested.
        submissions_root (Path): Path to the directory with prepared student submissions.
    """
    task_start = time.perf_counter()
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
                        print(f"❌ Error in {submission.name} for {task}: {e}")
                    pbar.update(1)

        generate_detailed_report(task, scenario_root)

    task_end = time.perf_counter()
    task_duration = task_end - task_start
    print(f"Finished grading all tasks in {task_duration:.2f} seconds.")

def grade_single_submission_wrapper(task, submission):
    try:
        grade_single_submission(task, submission)
        return submission.name, "Success"
    except Exception as e:
        return submission.name, f"Error: {e}"


def grade_single_submission(task: str, submission: Path) -> None:
    """
    Grades a single student submission for a specific task.

    Args:
        task (str): Name of the task to grade.
        student_dir (Path): Path to the student's submission directory.
    """

    run_task(task, submission, VenvManager(submission))

    # try:
    #     config = TASK_CONFIG.get(task_name)
    #     if not config:
    #         raise ValueError(f"Unknown task: {task_name}")

    #     # print("Submission path:", submission_path)

    #     # Determine the correct test directory based on scenario presence
    #     if config["scenario"]:
    #         # If a scenario is specified, use the submission directory name directly
    #         test_dir = submission.parent / f"{submission.name}"        
    #     else:
    #         test_dir = submission  # Use the original directory if no scenario

    #     test_script = test_dir / config["test_script"]
        
    #     # Get the Python path from the student's venv (replace with your logic)
    #     python_path = VenvManager(submission).get_python_path()
        
    #     # Build the test command
    #     args = ["-m", "unittest", test_script.name]
        
    #     # Run tests asynchronously
    #     proc = await asyncio.create_subprocess_exec(
    #         str(python_path),
    #         *args,
    #         stdout=asyncio.subprocess.PIPE,
    #         stderr=asyncio.subprocess.PIPE,
    #         cwd=str(submission)
    #     )
        
    #     stdout, stderr = await proc.communicate()
        
    #     if proc.returncode != 0:
    #         raise RuntimeError(f"Tests failed: {stderr.decode()}")
            
    #     # Process results here (e.g., save to report)
        
    # except Exception as e:
    #     print(f"Error grading {submission.name}: {str(e)}")


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
        asyncio.run(grade_all_submissions(tasks, path))
        
    
    
    


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Missing command.\n")
        print("Usage: python3 main.py {clean-submissions,prep-submissions,setup-venvs,run-tests}")
        print("Use `-h` or `--help` after a command for more info.")
        print()
        sys.exit(1)
    # print(Path(__file__).resolve())
    # preprocess_subs(Path(r"/Users/ebrahim_alaghbari/Documents/Portifolio/Automated-Marking/TemplatePythonModel"), Path(r"tests/Cleaned_Test_Files"))
    # grade_single_submission("Task_1", Path(r"D:\Portfolio\\Automated-Marking\Cleaned_suba\Portfolio 2 Upload Zone_c0101213"))
    # setup_venvs(Path(r"tests/Cleaned_Test_Files"))
    # grade_all_submissions(["Task_1","Task_2", "Task_3", "Task_4"], Path(r"D:\Portfolio\Automated-Marking\Cleaned_Submissions"))
    # setup_venvs(Path(r"/Users/ebrahim_alaghbari/Documents/Portifolio/Automated-Marking/tests/Cleaned_Test_Files"))
    main()
    # setup_virtualenvs(Path(r"D:\Portfolio\Automated-Marking\tests\Cleaned_Submissions - Copy (4) - Copy - Copy"))
    # all__(Path(r"D:\Portfolio\Automated-Marking\mock_zips"), Path(r"D:\Portfolio\Automated-Marking\TemplatePythonModel"))