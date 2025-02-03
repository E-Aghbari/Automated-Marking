import os, subprocess

class venvManager:
    def __init__(self, folderPath):
        self.__folerPath = folderPath
        self.__envPath = os.path.join(folderPath, "venv")

    def createVenv(self):
        venv = subprocess.run(["python3", "-m", "venv", self.__envPath])
    
    def pip(self):
        pipPath = os.path.join(self.__envPath, "Scripts", "pip,exe")
        return pipPath

    def python(self):
        pythonPath = os.path.join(self.__envPath, "Scripts", "python.exe")
        return pythonPath
    
    def installRequirements(self):
        pipPath = self.pip()
        subprocess.run([pipPath, "install", "-r", "requirements.txt"])

    def checkRequirements(self):
        pass

    def getFolderPath(self):
        return self.__folerPath

folder = venvManager(f"D:\Portfolio\\first-contributions")
# folder.createVenv()
folder.activate()
# print(folder.getFolderPath())
