from venv_manager import VenvManager
from test_manager import SubmissionPreprocessor, run_task
from pathlib import Path


def grade_single_submission(student_dir: Path):
    # Paths
    # teacher_dir = "teacher"
    # student_path = os.path.join("submissions", student_dir)    
    # 1. Initialize venv
    venv = VenvManager(student_dir)
    venv.create_venv()
    venv.install_requirements()
    
    # 3. Test Task_1 (example)
    try:
        # Override files and run test
        print(run_task("Task_2", student_dir, venv))
    except Exception as e:
        print(f"Error grading Task 1: {str(e)}")

if __name__ == "__main__":
    grade_single_submission(Path("tests/Cleaned_Test_Files/Portfolio 2 Upload Zone_c000000"))  # Grade a specific submission
