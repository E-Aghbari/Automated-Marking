from zipfile import ZipFile
import re
import shutil
from pathlib import Path

class CleanSubmission:
    def __init__(self, non_cleaned_submissions, cleaned_path=None):
        self.submissions_path = Path(non_cleaned_submissions)

        if cleaned_path:
            self.cleaned_path = Path(cleaned_path)
        else:
            self.cleaned_path = self.submissions_path.parent / "Cleaned_Submissions"

        self.keep_files = {"Task_1.py", "Task_2.py", "Task_3.py", "Task_4.py", "Task_5.py", "requirements.txt", "README.txt", "Helper.py", "notes.txt"}

    
    def unzip(self, zip_file_path):
        zip_path = Path(zip_file_path)

        # Step 1: Generate folder name from zip name using regex
        match = re.search(r"Portfolio 2 Upload Zone_c\d+", zip_path.stem)
        folder_name = match.group(0) if match else zip_path.stem
        extract_to = self.cleaned_path / folder_name

        # Step 2: Extract outer zip to a temporary temp folder
        temp_dir = self.submissions_path / f"temp_{zip_path.stem}"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir(parents=True)

        with ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Step 3: Unzip any nested zip files found in temp_dir (in-place)
        for nested_zip in list(temp_dir.rglob("*.zip")):
            with ZipFile(nested_zip, 'r') as z:
                z.extractall(nested_zip.parent)
            nested_zip.unlink()

        # Step 4: Clean up temp_dir:
        contents = list(temp_dir.iterdir())
        if len(contents) == 1 and contents[0].is_dir():
            # Only one folder inside temp_dir, just rename it
            if extract_to.exists():
                shutil.rmtree(extract_to)
            contents[0].rename(extract_to)
        else:
            # Multiple files/folders, move everything into extract_to
            extract_to.mkdir(parents=True, exist_ok=True)
            for item in contents:
                shutil.move(str(item), extract_to)

        # Step 5: Remove temp_dir
        temp_dir.rmdir()
        print(f"✅ Extracted: {zip_path.name} → {extract_to.name}")
        
    def unzip_all(self):
        for submission in self.submissions_path.glob("*.zip"):
            self.unzip(submission)

    def rename_submissions(self):
        for folder in self.submissions_path.iterdir():
            if folder.is_dir():
                match = re.search(r"(.+?_c\d+)", folder.name)
                if match:
                    new_name = match.group(1)
                    new_path = self.submissions_path / new_name
                    if folder != new_path:
                        folder.rename(new_path)

    def remove_unnecessary(self):
        if self.cleaned_path.exists():
            for folder in self.cleaned_path.iterdir():
                if folder.is_dir():
                    for item in folder.iterdir():
                        if item.is_file() and item.name not in self.keep_files:
                            item.unlink()
                        elif item.is_dir():
                            shutil.rmtree(item)

    def flatten_directory(self):
        if self.cleaned_path.exists():
            for submission_dir in self.cleaned_path.iterdir():
                if submission_dir.is_dir():
                    # Go one level deeper
                    for subitem in submission_dir.iterdir():
                        if subitem.is_dir():
                            for file in subitem.iterdir():
                                if file.is_file() and file.name in self.keep_files:
                                    destination = submission_dir / file.name
                                    if not destination.exists():
                                        file.replace(destination)
                        elif subitem.is_file() and subitem.name in self.keep_files:
                            # Already at top level, but still part of cleanup
                            continue
        else:
            print("The cleaned directory does not exist or has been moved.")

if __name__ == "__main__":
    folder = CleanSubmission("tests/Non_Cleaned_Test_Files")
    # folder.unzip(Path("tests/Non_Cleaned_Test_Files/Portfolio 2 Upload Zone_c444_attempt_2024-04-18-02-19-15_Portfolio2.zip"))
    # folder.unzip_all()
    folder.flatten_directory()
    folder.remove_unneccesary()