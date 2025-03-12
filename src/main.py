from venv_manager import VenvManager
from test_manager import SubmissionPreprocessor, run_task
from pathlib import Path
from report_generate import generate_detailed_report

# 1. Clean non-cleaned 
# 2. Set up venvs for
# 3. Copy Files and override tasks
# 4. 



def setup_venvs(submissions_root: Path):
    for submission in submissions_root.iterdir():
        if not submission.is_dir():
            continue
        submission_name = submission.name
        if submission_name.startswith("Portfolio"):
            venv = VenvManager(submission)
            venv.create_venv()
            venv.install_requirements()


def preprocess_subs(teacher_files: Path, submissions_root: Path):
    pre = SubmissionPreprocessor(teacher_files, submissions_root)
    pre.process_all_submissions()


def grade_all_submissions(task: str, submissions_root: Path):
    for submission in submissions_root.iterdir():
        grade_single_submission(task, submission)


def grade_single_submission(task: str, student_dir: Path):
    # Paths
    # teacher_dir = "teacher"
    # student_path = os.path.join("submissions", student_dir)    
    # # 1. Initialize venv
    # SubmissionPreprocessor(r'TemplatePythonModel', "tests/Cleaned_Test_Files").process_single_submission(student_dir)
    # venv = VenvManager(student_dir)
    # venv.create_venv()
    # venv.install_requirements()
    
    # 3. Test Task_1 (example)
    try:
        # Override files and run test
        print(run_task(task, student_dir, VenvManager(student_dir)))
        

        
    except Exception as e:
        print(f"Error grading {task}: {str(e)}")
    # generate_detailed_report(task, student_dir)

if __name__ == "__main__":
    print(Path(__file__).resolve())
    grade_single_submission("Task_1", Path(r"tests/Cleaned_Test_Files/Portfolio 2 Upload Zone_c000000"))
