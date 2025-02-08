from contextlib import contextmanager
import shutil
import os


TASK_CONFIG = {
    "Task_1": {
        "files_to_override": [],
        "test_script": "Testing_1.py"
    },
    "Task_2": {
        "files_to_override": ["Task_1.py"],
        "test_script": "Testing_2.py"
    },
    "Task_3": {
        "files_to_override": ["Task_1.py", "Task_2.py"],
        "test_script": "Testing_3.py"
    }
}

"""Create a custom context manager to override files when executing tasks."""
@contextmanager
def overrideFiles(teacherPath, studentPath, taskNames):
    
    ## Create backup directory
    backupPath = os.path.join(studentPath, "backup")
    os.makedirs(backupPath, exist_ok=True)

    ## Track the files that were backed up
    backups= []
    try:
        for task in taskNames:

            ## Prepare task paths
            studentFile = os.path.join(studentPath, task)
            backupFile = os.path.join(backupPath, f"{task}.bak")
            teacherFile = os.path.join(teacherPath, task)

            ## Back up student's task files in case they exist.
            if os.path.exists(studentFile):
                shutil.copy2(studentFile, backupFile)
                backups.append((backupFile, studentFile))
            else:
                print(f"Student {task} does not exist.")

            ## Override student's task file with teacher's version.
            if os.path.exists(teacherFile):
                shutil.copy2(teacherFile, studentFile)
            else:
                print(f"Teacher {task} does not exist.")

        yield
        
    finally:

        ## Restore the original student's task file after executing the test.
        for backup, student in backups:
            if os.path.exists(backupFile):
                shutil.move(backup, student)

def run_task(taskName, teacherPath, studentPath, venvManager):
    config = TASK_CONFIG[taskName]
    files_to_override = config["files_to_override"]
    test_script = os.path.join(studentPath, config["test_script"])

    with overrideFiles(teacherPath, studentPath, files_to_override):
       return venvManager.run_python(["-m", "unittest", test_script])
    

       