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
def overrideFiles(teacherPath, studentPath):
    try:
        for i in range(len(studentPath)):
            backupFile = f"{studentPath[i]}.bak"
            shutil.copy2(teacherPath[i], studentPath[i])
        
    finally:
        pass
        