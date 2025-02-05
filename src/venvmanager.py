import os
import subprocess
import sys

class venvManager:
    def __init__(self, folderPath):
        """Initialise folder and virtual environment path"""
        self.__folderPath = folderPath
        self.__envPath = os.path.join(folderPath, "venv")

    def createVenv(self):
        if not os.path.exists(self.__envPath):
            subprocess.run([sys.executable, "-m", "venv", self.__envPath])
    
    def pip(self):
        pipPath = os.path.join(self.__envPath, "Scripts", "pip.exe")
        return pipPath

    def python(self):
        pythonPath = os.path.join(self.__envPath, "Scripts", "python.exe")
        return pythonPath
    
    def installRequirements(self):
        pipPath = self.pip()
        reqPath = os.path.join(self.__folderPath, "requirements.txt")
        subprocess.run([pipPath, "install", "-r", reqPath])

    def validRequirements(self):
        pass

    # def checkRequirements(self):
    #     pipPath = self.pip()
    #     asdd = subprocess.run([pipPath, 'list'])
    #     print(asdd.stdout)

    def runPython(self, file):
        pythonPath = self.python()
        subprocess.run([pythonPath, file])


folder = venvManager(r"D:\Portfolio\first-contributions")
folder.createVenv()
# folder.checkRequirements()
# print(folder.getFolderPath())
