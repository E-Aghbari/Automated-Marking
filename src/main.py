from venv_manager import VenvManager
from test_manager import SubmissionPreprocessor, run_task
from config import TASK_CONFIG
from pathlib import Path
from report_generate import generate_detailed_report, generate_setup_report
import argparse
from clean_submission import CleanSubmission

# 1. Clean non-cleaned 
# 2. Set up venvs for
# 3. Copy Files and override tasks
# 4. Run tasks
# 5. Generate collated report 

def submission_cleaner(non_cleaned_root: Path):
    cl = CleanSubmission(non_cleaned_root)
    cl.unzip_all()
    cl.flatten_directory()
    cl.remove_unnecessary()
    return cl.cleaned_path


def setup_virtualenvs(submissions_root: Path):
    for submission in submissions_root.iterdir():
        if not submission.is_dir():
            continue
        submission_name = submission.name
        if submission_name.startswith("Portfolio"):
            venv = VenvManager(submission)
            venv.create_venv()
            venv.install_requirements()
            venv.save_log()
    generate_setup_report(submissions_root)


def preprocess_subs(teacher_files: Path, submissions_root: Path):
    pre = SubmissionPreprocessor(teacher_files, submissions_root)
    pre.process_all_submissions()


def grade_all_submissions(tasks: list, submissions_root: Path):
    
    for task in tasks:
        config = TASK_CONFIG.get(task)
        if not config:
            print(f"⚠️ Warning: Task '{task}' not found in TASK_CONFIG. Skipping...")
            continue

        for submission in submissions_root.iterdir():
            if not submission.is_dir():
                continue

            # If scenario is None, ensure submission is the original (no override in name)
            if config["scenario"] is None:
                if any(scenario["scenario"] in submission.name for scenario in TASK_CONFIG.values() if scenario["scenario"]):
                    continue  # Skip if it's an override folder
            else:                
                # If scenario exists, ensure it matches submission name
                if config["scenario"] not in submission.name:
                    continue
            grade_single_submission(task, submission)

        generate_detailed_report(task, submissions_root)


def grade_single_submission(task: str, student_dir: Path):

    try:
        print('student_dir', student_dir)
        # Override files and run test
        print(run_task(task, student_dir, VenvManager(student_dir)))
        
    except Exception as e:
        print(f"Error grading {task}: {str(e)}\n")
    # generate_detailed_report(task, student_dir)

def main():
    parser = argparse.ArgumentParser(prog="Automatic Marking",description="Student Submission Automation Tool")
    subparser = parser.add_subparsers(
        dest="command",
        title="Available Commands",
        description="Run a specific step in the marking pipeline",
        required=True
    )


    ## add optional arg for cleaned path
    clean_submissions = subparser.add_parser("clean-submissions", help="Unzip and clean students' submissions.")
    clean_submissions.add_argument("--path", required=True, help="Absolute path to the folder containing non-cleaned submissions.")


    ## think if you going to add option to move testing files like images
    pre_submissions = subparser.add_parser("prep-submissions", help="Copy testing files and override tasks")
    pre_submissions.add_argument("--tests-path", required=True, help="Absolute path to the folder containing teacher's tests and tasks files.")
    pre_submissions.add_argument("--path", required=True, help="Absolute path to the folder containing cleaned submissions.")

    setup_venvs = subparser.add_parser("setup-venvs", help="Set up virtual environments for submissions.")
    setup_venvs.add_argument("--path", required=True, help="Absolute path to the folder containing cleaned submissions.")

    run_tests = subparser.add_parser("run-tests", help="Run unit tests for all students.")
    run_tests.add_argument("--path", required=True, help="Absolute path to the folder containing cleaned and prepared submissions.")
    run_tests.add_argument("--tasks", required=True, help="Type the tasks that need to be tested.")

    args = parser.parse_args()
    path = Path(args.path)

    if args.command == "clean-submissions":
        submission_cleaner(path)

    elif args.command == "prep-submissions":
        test_path = Path(args.tests_path)
        preprocess_subs(test_path, path)

    elif args.command == "setup-venvs":
        setup_virtualenvs(path)

    elif args.command == "run-tests":
        tasks = (args.tasks).split()
        grade_all_submissions(tasks, path)
        
    
    
    


if __name__ == "__main__":
    # print(Path(__file__).resolve())
    # preprocess_subs(Path(r"/Users/ebrahim_alaghbari/Documents/Portifolio/Automated-Marking/TemplatePythonModel"), Path(r"tests/Cleaned_Test_Files"))
    # grade_single_submission("Task_1", Path(r"tests/Cleaned_Test_Files/Portfolio 2 Upload Zone_c444"))
    # setup_venvs(Path(r"tests/Cleaned_Test_Files"))
    # grade_all_submissions(["Task_1"], Path(r"tests/Cleaned_Test_Files"))
    # setup_venvs(Path(r"/Users/ebrahim_alaghbari/Documents/Portifolio/Automated-Marking/tests/Cleaned_Test_Files"))
    main()