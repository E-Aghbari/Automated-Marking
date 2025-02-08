from venv_manager import VenvManager
from test_manager import overrideFiles, run_task


def grade_single_submission(student_dir: str):
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
        print(run_task("Task_1", r'/Users/ebrahim_alaghbari/Documents/Portifolio/Automated-Marking/tests/TemplatePythonModel', student_dir, venv))
    except Exception as e:
        print(f"Error grading Task 1: {str(e)}")

if __name__ == "__main__":
    grade_single_submission(r'/Users/ebrahim_alaghbari/Library/CloudStorage/OneDrive-CardiffUniversity/CM3203 - Individual Project/Portfolio 2 Marking Support/TemplatePythonModel')  # Grade a specific submission
