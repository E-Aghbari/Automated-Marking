import os
import subprocess

class venvManager:
    def __init__(self, folderPath):
        """Initialise folder and virtual environment path"""
        self.__folderPath = folderPath
        self.__envPath = os.path.join(folderPath, "venv")

    def createVenv(self):
        subprocess.run(["python3", "-m", "venv", self.__envPath])
    
    def pip(self):
        pipPath = os.path.join(self.__envPath, "Scripts", "pip.exe")
        return pipPath

    def python(self):
        pythonPath = os.path.join(self.__envPath, "Scripts", "python.exe")
        return pythonPath
    
    def installRequirements(self):
        pipPath = self.pip()
        subprocess.run([pipPath, "install", "-r", "requirements.txt"])

    def validRequirements(self):
        pass

    def runPython(self, file):
        pythonPath = self.python()
        subprocess.run([pythonPath, file])


folder = venvManager(r"C:/Users/Ghabr/OneDrive - Cardiff University/2nd Year/CM2203 Informatics/Portfolio 2/TemplatePython")
folder.createVenv()
# print(folder.getFolderPath())
