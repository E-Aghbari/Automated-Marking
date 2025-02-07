from contextlib import contextmanager
import shutil
import os


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

def testTask1():
    pass

def testTask2():
    pass

def testTask3():
    pass

def testTask4():
    pass

def testTask5():
    pass
