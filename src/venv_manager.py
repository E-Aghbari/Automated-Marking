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
            print(f"Creating venv within {self._folderPath.name} directory.")
            result = subprocess.run(
                [sys.executable, "-m", "venv", str(self._envPath)],
                capture_output= True,
                text=True
            )
            if result.returncode != 0:
                raise RuntimeError (f"Failed to create venv: {result.stderr}")
            print("venv has successfully been created.\n")

        else:
            print(f"venv has already been created for {self._folderPath.name}.\n")
    
    ## Venv's pip path for execution
    def get_pip_path(self) -> Path:
        if not self._envPath.exists():
            raise FileNotFoundError("Virtual environment not created. Run create_venv() first.\n")
        
        if sys.platform == 'win32':
            pipPath = self._envPath / "Scripts" / "pip.exe"
        else:
            pipPath = self._envPath / "bin" / "pip"
        
        return pipPath

    ## Venv's python path for execution
    def get_python_path(self) -> Path:
        self.get_original_submission()
        print(self._envPath)
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
        pipPath = self.get_pip_path()

        if not reqPath.exists():
            print(f"⚠️ Warning: No 'requirements.txt' found in {self._folderPath}. Skipping dependency installation.\n")
            return 
            
        print("📦 Installing dependencies for virtual environment...")
        result = subprocess.run(
            [str(pipPath), "install", "-r", str(reqPath)],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"❌ Failed to install dependencies: {result.stderr}\n")
        else:
            print("✅ Dependencies installed successfully.\n")
    
        
    def valid_requirements(self):
        pass

    def get_original_submission(self) -> Path:

        original_name = self._folderPath.name

        if original_name.endswith("_Task1_Override"):

            original_name = original_name.replace("_Task1_Override", "")
            self._envPath = self._folderPath.parent / original_name / "venv"

        elif original_name.endswith("_Task1_Task2_Override"):

            original_name = original_name.replace("_Task1_Task2_Override", "")
            self._envPath = self._folderPath.parent / original_name / "venv"
        

        return self._folderPath.parent / original_name
            


    ## Run program using venv's python
    def run_python(self, args, cwd) -> str:
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
    folder = VenvManager(r"tests/Cleaned_Test_Files/Portfolio 2 Upload Zone_c666666_Task1_Override")
    folder.run_python("Task_2", r"tests/Cleaned_Test_Files/Portfolio 2 Upload Zone_c666666_Task1_Override")
