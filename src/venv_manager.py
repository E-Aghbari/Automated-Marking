import os
import subprocess
import sys
from pathlib import Path


"""Creating and managing virtual environment"""
class VenvManager:

    ## Initialise the folder and virtual environment path
    def __init__(self, folderPath: Path):
        self._folderPath = Path(folderPath).resolve()
        self._envPath = self._folderPath / "venv"

    ## Create virtual environment in the submission directory as 'venv'
    def create_venv(self):
        if not self._envPath.exists():
            print("Creating venv within student's directory.")
            result = subprocess.run(
                [sys.executable, "-m", "venv", str(self._envPath)],
                capture_output= True,
                text=True
            )
            if result.returncode != 0:
                raise RuntimeError (f"Failed to create venv: {result.stderr}")
            print("venv has successfully been created.")

        else:
            print("venv already created.")
    
    ## Venv's pip path for execution
    def get_pip_path(self):
        if not self._envPath.exists():
            raise FileNotFoundError(f"Virtual environment not created. Run create_venv() first.")
        
        if sys.platform == 'win32':
            pipPath = self._envPath / "Scripts" / "pip.exe"
        else:
            pipPath = self._envPath / "bin" / "pip"
        
        return pipPath

    ## Venv's python path for execution
    def get_python_path(self):
        if not self._envPath.exists():
            raise FileNotFoundError(f"Virtual environment not created. Run create_venv() first.")
        
        if sys.platform == 'win32':
            pythonPath = self._envPath / "Scripts" / "python.exe"
        else: 
            pythonPath = self._envPath / "bin" / "python"
            
        return pythonPath
    
    ## Install dependencies specified within 'requirements.txt'
    def install_requirements(self):
        reqPath = self._folderPath / "requirements.txt"
        if not reqPath.exists():
            raise FileNotFoundError(f"Requirements.txt file does not exist!")
        
        pipPath = self.get_pip_path()
        result = subprocess.run(
            [str(pipPath), "install", "-r", str(reqPath)],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError (f"Failed to install dependencies: {result.stderr}") 
        
    def valid_requirements(self):
        pass

    ## Run program using venv's python
    def run_python(self, args, cwd):
        pythonPath = str(self.get_python_path())
        command = [pythonPath] + args
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd = str(cwd) if cwd else None
        )

        if result.returncode != 0:
            raise RuntimeError (f"Failed to run python: {result.stderr}")
        
        return result.stdout

if __name__ == "__main__":
    folder = VenvManager(r"D:/nasdfa/my/borther")
    folder.create_venv()
