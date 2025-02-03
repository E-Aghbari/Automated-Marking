import os, subprocess

class venvManager:
    def __init__(self, folderPath):
        self.__folerPath = folderPath
        self.__envPath = os.path.join(folderPath, "venv")

    def createVenv(self):
        venv = subprocess.run(["python3", "-m", "venv", self.__envPath])
    
    def activate(self):
        venvFolder = os.path.join(self.__folerPath, "venv", "Scripts", "activate")
        subprocess.run(["call", venvFolder], shell=True, capture_output=True)
    
    def deactivate(self):
        subprocess.run(["deactivate"])
    
    def installRequirements(self):
        pass

    def checkRequirements(self):
        pass

    def getFolderPath(self):
        return self.__folerPath

folder = venvManager(f"D:\Portfolio\\first-contributions")
# folder.createVenv()
folder.activate()
# print(folder.getFolderPath())
