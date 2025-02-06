import os
import subprocess
import sys


"""Creating and managing virtual environment"""
class VenvManager:

    ## Initialise the folder and virtual environment path
    def __init__(self, folderPath):
        self._folderPath = folderPath
        self._envPath = os.path.join(folderPath, "venv")

    ## Create virtual environment in the submission directory as 'venv'
    def create_venv(self):
        if not os.path.exists(self._envPath):
            result = subprocess.run(
                [sys.executable, "-m", "venv", self._envPath],
                capture_output= True,
                text=True
            )
            if result.returncode != 0:
                raise RuntimeError (f"Failed to create venv: {result.stderr}")
    
    ## Venv's pip path for execution
    def get_pip_path(self):
        if not os.path.exists(self._envPath):
            raise FileNotFoundError(f"Virtual environment not created. Run create_venv() first.")
        
        if sys.platform == 'win32':
            pipPath = os.path.join(self._envPath, "Scripts", "pip.exe")
        else:
            pipPath = os.path.join(self._envPath, "bin", "pip")
        
        return pipPath

    ## Venv's python path for execution
    def get_python_path(self):
        if not os.path.exists(self._envPath):
            raise FileNotFoundError(f"Virtual environment not created. Run create_venv() first.")
        
        if sys.platform == 'win32':
            pythonPath = os.path.join(self._envPath, "Scripts", "python.exe")
        else: 
            pythonPath = os.path.join(self._envPath, "bin", "python")
            
        return pythonPath
    
    ## Install dependencies specified within 'requirements.txt'
    def install_requirements(self):
        reqPath = os.path.join(self._folderPath, "requirements.txt")
        if not os.path.exists(reqPath):
            raise FileNotFoundError(f"Requirements.txt file does not exist!")
        
        pipPath = self.get_pip_path()
        result = subprocess.run(
            [pipPath, "install", "-r", reqPath],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError (f"Failed to install dependencies: {result.stderr}") 
        
    def valid_requirements(self):
        pass

    ## Run program using venv's python
    def run_python(self, file):
        pythonPath = self.get_python_path()
        result = subprocess.run(
            [pythonPath, file],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError (f"Failed to run python: {result.stderr}")
        
        return result.stdout

# folder = venvManager(r"D:\Portfolio\first-contributions")

