from venv_manager import VenvManager
from test_manager import SubmissionPreprocessor, run_task
from pathlib import Path
from report_generate import generate_detailed_report

def grade_single_submission(task, student_dir: Path):
    # Paths
    # teacher_dir = "teacher"
    # student_path = os.path.join("submissions", student_dir)    
    # # 1. Initialize venv
    # SubmissionPreprocessor(r'TemplatePythonModel', student_dir).process_single_submission(student_dir)
    venv = VenvManager(student_dir)
    venv.create_venv()
    venv.install_requirements()
    
    # 3. Test Task_1 (example)
    try:
        # Override files and run test
        print(run_task(task, student_dir, venv))

        
    except Exception as e:
        print(f"Error grading {task}: {str(e)}")
    generate_detailed_report(1, r"tests\Cleaned_Test_Files\Portfolio 2 Upload Zone_c000000")

def grade_all_submissions(task, submissions_dir = r"..\tests\Cleaned_Test_Files"):
    sub_dir = Path(submissions_dir)
    
    for submission in sub_dir.iterdir():
        grade_single_submission(task, submission)

        generate_detailed_report(1, submission)


if __name__ == "__main__":
    grade_single_submission("Task_1",Path(r"tests\Cleaned_Test_Files\Portfolio 2 Upload Zone_c000000"))  # Grade a specific submission
