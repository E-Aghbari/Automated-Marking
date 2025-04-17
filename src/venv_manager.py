import os
import subprocess
import sys
from pathlib import Path
from packaging import requirements
import requests, chardet
from config import TASK_CONFIG

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read(2048)
    result = chardet.detect(raw_data)
    return result.get("encoding", "utf-8")

"""Creating and managing virtual environment"""
class VenvManager:

    ## Initialise the folder and virtual environment path
    def __init__(self, folderPath: Path):
        self._folderPath = Path(folderPath).resolve()
        self._envPath = self._folderPath / "venv"
        self.requirements_path = self._folderPath / "requirements.txt"
        self.use_global_env = False  
        self._log_lines = []

    ## Create virtual environment in the submission directory as 'venv'
    def create_venv(self):
        self.get_original_submission()
        if not self._envPath.exists():
            print(f"Creating venv within {self._folderPath.name} directory.")
            result = subprocess.run(
                [sys.executable, "-m", "venv", str(self._envPath)],
                capture_output= True,
                text=True
            )

            if result.returncode != 0:
                print(f"Failed to create venv: {result.stderr}")
                print("⚠️ Falling back to global environment.\n")
                self.use_global_env = True
                self.log("Creating venv; FAILED: Could not create virtual environment. Fallback to global environment activated.")
                return False
            
            print("venv has successfully been created.\n")
            self.log("Creating venv; SUCCESS: Virtual environment created successfully.")
            return True

        else:
            print(f"venv has already been created for {self._folderPath.name}.\n")
            self.log("Creating venv; SUCCESS: venv already existed.")
            return True
    
    ## Venv's pip path for execution
    def get_pip_path(self) -> Path:
        if self.use_global_env:
            print("⚠️ Using global pip.")
            return Path(sys.executable).parent / ("pip.exe" if sys.platform == "win32" else "pip")
        
        self.get_original_submission()

        print(self._envPath)

        if not self._envPath.exists():
            raise FileNotFoundError("Virtual environment not created. Run create_venv() first.\n")
        
        if sys.platform == 'win32':
            pipPath = self._envPath / "Scripts" / "pip.exe"
        else:
            pipPath = self._envPath / "bin" / "pip"
        
        return pipPath

    ## Venv's python path for execution
    def get_python_path(self) -> Path:
        
        if self.use_global_env:
            print("⚠️ Using global Python.")
            return Path(sys.executable)
        
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

        self.valid_requirements(self.requirements_path)

        reqPath = self.requirements_path
        pipPath = self.get_pip_path()

            
        print("📦 Installing dependencies for virtual environment...")
        result = subprocess.run(
            [str(pipPath), "install", "-r", str(reqPath)],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"❌ Failed to install dependencies: {result.stderr}\n")
            self.log(f"Dependencies Installation; FAILED: Dependency installation failed. Error: {result.stderr.strip()}")
        else:
            print("✅ Dependencies installed successfully.\n")
            self.log("Dependencies Installation; SUCCESS: All dependencies installed successfully.")
    

    def get_original_submission(self) -> Path:

        original_name = self._folderPath.name

        # if original_name.endswith("_Task1_Override"):

        #     original_name = original_name.replace("_Task1_Override", "")
        #     self._envPath = self._folderPath.parent / original_name / "venv"

        # elif original_name.endswith("_Task1_Task2_Override"):

        #     original_name = original_name.replace("_Task1_Task2_Override", "")
        #     self._envPath = self._folderPath.parent / original_name / "venv"
        

        # return self._folderPath.parent / original_name
        # original_name = self._folderPath.name

    # Dynamically check all scenarios in TASK_CONFIG
        for config in TASK_CONFIG.values():
            scenario = config.get("scenario")
            if scenario and original_name.endswith(f"_{scenario}"):
                # Strip the scenario suffix from the folder name
                original_name = original_name.removesuffix(f"_{scenario}")
                self._envPath = self._folderPath.parent / original_name / "venv"
                break  # stop after finding the first matching scenario

        return self._folderPath.parent / original_name
            


    ## Run program using venv's python
    def run_python(self, args, cwd) -> str:
        pythonPath = str(self.get_python_path())
        command = [pythonPath] + args
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd = str(cwd) if cwd else None,
            timeout=15.0
        )

        if result.returncode != 0:
            raise RuntimeError (f"Failed to run python: {result.stderr}")
        
        return result.stdout
    
    def valid_requirements(self, req_file):

        print(f'\nValidating requirements.txt for {self._folderPath.name}')

        if not req_file.exists():
            print(f"⚠️ Warning: No 'requirements.txt' found in {self._folderPath.name}. Skipping dependency installation.")
            self.log("Requirements Validation; FAILED: requirements.txt not found. Default requirements will be used.")
            self._write_cleaned_requirements()
            return 

        detected_encoding = detect_encoding(req_file)

        with open(req_file, encoding=detected_encoding) as r:
            lines = [line.strip() for line in r]

            if len(lines) > 15:
                    print(f"⚠️ {len(lines)} packages listed — likely copied from global environment.")
                    self.log("Requirements Validation; FAILED: More than 15 packages detected. Possibly copied from global environment. Default requirements used.")
                    self._write_cleaned_requirements()
                    return                    
                    
    
            for line in lines:
                if not self.validate_format(line):
                    print(f"{line} in student's requirements.txt has format issues.")
                    self.log(f"Requirements Validation; FAILED: Requirement format invalid: {line}. Default requirements used.")
                    self._write_cleaned_requirements()
                    return

                try:
                    req = requirements.Requirement(line)
                    package_name = req.name
                    if not self.package_exists(package_name):
                        print(f"{package_name} in student's requirements.txt does not exist in PyPI library.")
                        self.log(f"Requirements Validation; FAILED: Package '{package_name}' not found on PyPI. Default requirements used.")
                        self._write_cleaned_requirements()
                        return
                                       
                except Exception as e:
                    print(line, f"Unexpected error: {str(e)}")
                    self.log(f"Requirements Validation; FAILED: Unexpected error while validating requirements {e}. Default requirements used.")
                    self._write_cleaned_requirements()
                    return

            print("✅ All requirement lines are valid.")
            self.log("Requirements Validation; SUCCESS: requirements.txt validated successfully.")
            self.requirements_path = req_file
            
    def validate_format(self, line):
        try:
            requirements.Requirement(line)
            print(f"{line} is correct parsed")
            return True
        except requirements.InvalidRequirement:
            print(f"{line} is wrong parsed")
            return False
    
    def package_exists(self, package_name):
        response = requests.get(f"https://pypi.org/pypi/{str(package_name)}/json")
        return response.status_code == 200
    
    def _write_cleaned_requirements(self):
        print("⚠️ Invalid requirements found. Using known good packages instead.")

        corrected_lines = [
                "numpy==2.2.2",
                "opencv-python==4.11.0.86",
                "sewar==0.4.6",
                "pillow==11.1.0"
            ]
        cleaned_path = self._folderPath / "requirements_cleaned.txt"
        with cleaned_path.open("w") as f:
            f.write("\n".join(corrected_lines) + "\n")

        self.requirements_path = cleaned_path
        print(f"📄 Cleaned requirements written to: {cleaned_path}")
    
    def log(self, message):
        self._log_lines.append(message)

    def save_log(self):
        log_path = self._folderPath / "log.txt"
        with log_path.open("w") as f:
            for line in self._log_lines:
                f.write(line + "\n")

if __name__ == "__main__":
    # folder = VenvManager(r"tests/Cleaned_Test_Files/Portfolio 2 Upload Zone_c666666_Task1_Override")
    # folder.run_python("Task_2", r"tests/Cleaned_Test_Files/Portfolio 2 Upload Zone_c666666_Task1_Override")
    vm = VenvManager(r'/Users/ebrahim_alaghbari/Documents/Portifolio/Automated-Marking/tests/Cleaned_Test_Files/Portfolio 2 Upload Zone_c000000_Task1_Override')
    vm.get_pip_path()
