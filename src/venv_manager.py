"""
Virtual Environment Manager for Automated Marking

This module defines the VenvManager class, which handles:
- Creating and managing virtual environments for student submissions.
- Validating and installing dependencies listed in requirements.txt.
- Running Python scripts inside the isolated managed environment.
- Logging all setup and execution steps for traceability.
"""
import subprocess
import sys
from pathlib import Path
from packaging import requirements
import requests, chardet
from config import TASK_CONFIG, DEFAULT_DEPENDENCIES
import time

# Detects the requirements.txt encoding. 
def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read(2048)
    result = chardet.detect(raw_data)
    return result.get("encoding", "utf-8")

class VenvManager:
    """
    A class that automates virtual environment setup and package installation for isolated execution
    of student code submissions. It ensures consistent environments and logs all actions.
    """

    def __init__(self, folderPath: Path):
        """
        Initialize the VenvManager with the target folder path. Sets up paths for the virtual environment,
        requirements file, and flags for environment usage and saves loggings.
        """
        self._folderPath = Path(folderPath).resolve()
        self._envPath = self._folderPath / "venv"
        self.requirements_path = self._folderPath / "requirements.txt"
        self.use_global_env = False  
        self._log_lines = []
        
    def create_venv(self):
        """
        Create a virtual environment in the submission directory named 'venv'.
        Attempts to use 'uv' for faster creation; falls back to built-in venv if 'uv' fails.
        Logs success or failure accordingly.
        """
        self.get_original_submission()

        # Check if venv already exists
        if not self._envPath.exists():
            try:
                # Try to create venv using 'uv'
                result = subprocess.run(
                    ['uv', "venv", str(self._envPath)],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    raise RuntimeError(result.stderr)
            except Exception as e:
                # Fallback to built-in venv if 'uv' fails
                print(f"⚠️ 'uv' failed, falling back to built-in venv. Error: {e}")
                result = subprocess.run(
                    [sys.executable, "-m", "venv", str(self._envPath)],
                    capture_output=True,
                    text=True
                )
            # Handle venv creation result
            if result.returncode != 0:
                self.use_global_env = True
                # Log failure and fallback
                self.log("Creating venv; FAILED: Could not create virtual environment. Fallback to global environment activated.")
                return False
            # Log success
            self.log("Creating venv; SUCCESS: Virtual environment created successfully.")
            return True
        else:
            # venv already exists; log and return
            self.log("Creating venv; SUCCESS: venv already existed.")
            return True
    
    def get_pip_path(self) -> Path:
        """
        Return the path to the pip executable within the virtual environment.
        Falls back to global pip if the virtual environment is not used.
        Handles both Windows and Unix-like systems.
        """
        # Fallback to global interpreter logic
        if self.use_global_env:
            return Path(sys.executable).parent / ("pip.exe" if sys.platform == "win32" else "pip")
        
        self.get_original_submission()

        # Exception handling if the virtual environment is not found
        if not self._envPath.exists():
            raise FileNotFoundError("Virtual environment not created. Run create_venv() first.\n")
        
        # Path construction for Windows vs. Unix systems
        if sys.platform == 'win32':
            pipPath = self._envPath / "Scripts" / "pip.exe"
        else:
            pipPath = self._envPath / "bin" / "pip"
        
        return pipPath

    def get_python_path(self) -> Path:
        """
        Return the path to the python executable within the virtual environment.
        If fallback to global environment is active, return the global Python executable.
        Handles platform-specific paths for Windows and Unix-like systems.
        """
        # Fallback to global interpreter logic
        if self.use_global_env:
            return Path(sys.executable)
        
        self.get_original_submission()

        # Exception handling if the virtual environment is not found
        if not self._envPath.exists():
            raise FileNotFoundError(f"Virtual environment not created. Run create_venv() first.")
        
        # Path construction for Windows vs. Unix systems
        if sys.platform == 'win32':
            pythonPath = self._envPath / "Scripts" / "python.exe"
        else: 
            pythonPath = self._envPath / "bin" / "python"
            
        return pythonPath
    
    def install_requirements(self):
        """
        Validate the requirements.txt file and install dependencies using 'uv pip' for speed.
        If 'uv pip' fails, fallback to standard pip installation.
        Deletes cleaned requirements file after installation if used.
        Logs success or failure of the installation process.
        """
        # Validate requirements file before installation
        self.valid_requirements(self.requirements_path)

        reqPath = self.requirements_path

        try:
            # Attempt to install dependencies using 'uv pip' for faster installation
            result = subprocess.run(
                ["uv", "pip", "install", "-r", str(reqPath), "--python", str(self.get_python_path())],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                raise RuntimeError(result.stderr)
            else:
                if reqPath.name == "requirements_cleaned.txt":
                    try:
                        reqPath.unlink()
                    except Exception as e:
                        print(f"Could not delete requirements_cleaned.txt. Error: {e}")

        except Exception as e:
            # Fallback to standard pip installation if 'uv pip' fails
            print(f"⚠️ 'uv pip' failed, falling back to standard pip. Error: {e}")

            pipPath = self.get_pip_path()

            result = subprocess.run(
                [str(pipPath), "install", "-r", str(reqPath)],
                capture_output=True,
                text=True
            )

        # Log the result of the installation process
        if result.returncode != 0:

            self.log(f"Dependencies Installation; FAILED: Dependency installation failed. Error: {result.stderr.strip()}")
        else:

            self.log("Dependencies Installation; SUCCESS: All dependencies installed successfully.")
    

    def get_original_submission(self) -> Path:
        """
        Determine the original submission folder by removing any scenario suffixes defined in TASK_CONFIG.
        Adjusts the virtual environment path accordingly to point to the original submission's venv.
        """
        original_name = self._folderPath.name
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
        """
        Run a Python script with given arguments inside the virtual environment.
        Executes subprocess with timeout and captures output.
        Raises RuntimeError if execution fails.
        """
        # start = time.perf_counter()
        pythonPath = sys.executable
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
        # end = time.perf_counter()
        # print(f"Duration {end - start}")
        
        return result.stdout
    
    def valid_requirements(self, req_file: Path):
        """
        Validate the requirements.txt file by checking:
        - File existence.
        - Number of packages (max 15).
        - Format of each requirement line.
        - Package existence on PyPI.
        Logs any validation failures and writes default requirements if validation fails.
        """

        # Check if the file exists.
        if not req_file.exists():
            # Fallback: requirements.txt not found, use default requirements.
            self.log("Requirements Validation; FAILED: requirements.txt not found. Default requirements will be used.")
            self._write_cleaned_requirements()
            return 

        # Detect the file's encoding.
        detected_encoding = detect_encoding(req_file)

        with open(req_file, encoding=detected_encoding) as r:
            lines = [line.strip() for line in r]

            # Before checking number of packages.
            if len(lines) > 15:
                # Fallback: too many packages, use default requirements.
                self.log("Requirements Validation; FAILED: More than 15 packages detected. Possibly copied from global environment. Default requirements used.")
                self._write_cleaned_requirements()
                return                    
            
            # Before validating each requirement's format.
            for line in lines:
                if not self.validate_format(line):
                    # Fallback: invalid requirement format, use default requirements.
                    self.log(f"Requirements Validation; FAILED: Requirement format invalid: {line}. Default requirements used.")
                    self._write_cleaned_requirements()
                    return

                try:
                    req = requirements.Requirement(line)
                    package_name = req.name
                    # Before checking package availability on PyPI.
                    if not self.package_exists(package_name):
                        # Fallback: package not on PyPI, use default requirements.
                        self.log(f"Requirements Validation; FAILED: Package '{package_name}' not found on PyPI. Default requirements used.")
                        self._write_cleaned_requirements()
                        return
                                   
                except Exception as e:
                    # Fallback: unexpected error, use default requirements.
                    self.log(f"Requirements Validation; FAILED: Unexpected error while validating requirements {e}. Default requirements used.")
                    self._write_cleaned_requirements()
                    return

            # All checks passed.
            self.log("Requirements Validation; SUCCESS: requirements.txt validated successfully.")
            self.requirements_path = req_file
            
    def validate_format(self, line: str) -> bool:
        """
        Check if a requirement line is syntactically valid according to packaging standards.
        """
        try:
            requirements.Requirement(line)

            return True
        except requirements.InvalidRequirement:

            return False
    
    def package_exists(self, package_name: str) -> bool:
        """
        Check if the given package exists on PyPI using a live API request.
        """
        response = requests.get(f"https://pypi.org/pypi/{str(package_name)}/json")
        return response.status_code == 200
    
    def _write_cleaned_requirements(self):
        """
        Write a default set of dependencies to 'requirements_cleaned.txt' in the submission folder.
        This is used as a fallback when the original requirements.txt is invalid or missing.
        """
        cleaned_path = self._folderPath / "requirements_cleaned.txt"
        with cleaned_path.open("w") as f:
            f.write("\n".join(DEFAULT_DEPENDENCIES) + "\n")

        self.requirements_path = cleaned_path
    
    def log(self, message):
        """
        Append a message to the internal log list.
        """
        self._log_lines.append(message)

    def save_log(self):
        """
        Write all log messages to a log.txt file in the submission directory.
        """
        log_path = self._folderPath / "log.txt"
        with log_path.open("w") as f:
            for line in self._log_lines:
                f.write(line + "\n")
        
if __name__ == "__main__":
    # folder = VenvManager(r"tests/Cleaned_Test_Files/Portfolio 2 Upload Zone_c666666_Task1_Override")
    # folder.run_python("Task_2", r"tests/Cleaned_Test_Files/Portfolio 2 Upload Zone_c666666_Task1_Override")
    vm = VenvManager(r'D:\Portfolio\Automated-Marking\Cleaned\Portfolio 2 Upload Zone_c0101227')
    vm.run_python(['-m', 'unittest', 'Testing_1.py'],vm._folderPath)
