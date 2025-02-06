from contextlib import contextmanager
import shutil
import os

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

@contextmanager
def overrideFiles(teacherPath, studentPath, taskNames):
    backupPath = os.path.join(studentPath, "backup")
    if not os.path.exists(backupPath):
        os.mkdir(backupPath)
    
    try:
        for i in range(len(taskNames)):

            studentFile = os.path.join(studentPath, taskNames[i])
            backupFile = os.path.join(backupPath, f"{taskNames[i]}.bak")
            shutil.copy2(studentFile, backupFile)

            teacherFile = os.path.join(teacherPath, taskNames[i])
            shutil.copy2(teacherFile, studentPath)

        yield
        
    finally:
        for i in range(len(taskNames)):
            backupFile = os.path.join(backupPath, f"{taskNames[i]}.bak")
            shutil.move(backupFile, studentPath)
        
