"""
CleanSubmission Script

This module defines the CleanSubmission class, which automates the process of preparing student submissions
for automated grading. It handles the extraction of nested zip files, cleaning irrelevant files, renaming
directories, and flattening directory structures.
"""
from zipfile import ZipFile
import re
import shutil
from pathlib import Path
from tqdm import tqdm
from config import KEEP_FILES
from concurrent.futures import ThreadPoolExecutor, as_completed

class CleanSubmission:
    """
    A utility class to clean and organise student submission folders by unzipping, flattening, and removing unnecessary files.
    """
    def __init__(self, non_cleaned_submissions: str | Path, cleaned_path: str | Path =None):
        """
        Initialises paths for raw and cleaned submissions.

        Args:
            non_cleaned_submissions (str or Path): Directory containing raw zipped submissions.
            cleaned_path (str or Path, optional): Target directory for cleaned submissions.
        """
        # Initialise the path containing the raw submission zip files
        self.submissions_path = Path(non_cleaned_submissions)

        # Set the cleaned submissions directory, use provided or default to sibling folder
        if cleaned_path:
            self.cleaned_path = Path(cleaned_path)
        else:
            self.cleaned_path = self.submissions_path.parent / "Cleaned_Submissions"

        # List of files to keep during cleaning process, imported from config
        self.keep_files = KEEP_FILES

    
    def unzip(self, zip_file_path: str | Path) -> None:
        """
        Extracts a given zip file, handles nested zips, and relocates the extracted contents to the cleaned directory.

        Args:
            zip_file_path (str or Path): Path to the zip file to be extracted.
        """
        zip_path = Path(zip_file_path)

        # Extract student name or folder name from zip file name using regex pattern
        match = re.search(r"Portfolio 2 Upload Zone_c\d+", zip_path.stem)
        folder_name = match.group(0) if match else zip_path.stem
        extract_to = self.cleaned_path / folder_name

        # Create a temporary directory inside the raw submissions folder to extract initial zip
        temp_dir = self.submissions_path / f"temp_{zip_path.stem}"
        # Remove temp directory if it already exists to avoid conflicts
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        # Create the temp directory fresh
        temp_dir.mkdir(parents=True)

        # Extract the main zip file into the temporary directory
        with ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Search for nested zip files inside the temp directory and extract them
        for nested_zip in list(temp_dir.rglob("*.zip")):
            with ZipFile(nested_zip, 'r') as z:
                # Extract nested zip contents into the same folder as the nested zip
                z.extractall(nested_zip.parent)
            # Remove the nested zip file after extraction
            nested_zip.unlink()

        # List contents of temp directory after extraction and nested extraction
        contents = list(temp_dir.iterdir())
        if len(contents) == 1 and contents[0].is_dir():
            # If only one folder inside temp_dir, rename/move it to the target cleaned directory
            if extract_to.exists():
                # Remove existing target directory if present to avoid conflicts
                shutil.rmtree(extract_to)
            
            try:
                # Attempt to rename the folder directly
                contents[0].rename(extract_to)
            except Exception as e:
                # If rename fails (e.g., across filesystems), fallback to shutil.move
                shutil.move(str(contents[0]), str(extract_to))

        else:
            # If multiple files/folders, create target directory and move each item individually
            extract_to.mkdir(parents=True, exist_ok=True)
            for item in contents:
                dest_path = extract_to / item.name
                # If destination exists, delete it before moving to avoid conflicts
                if dest_path.exists():
                    if dest_path.is_file():
                        dest_path.unlink() 
                    else:
                        shutil.rmtree(dest_path) 

                # Move the item to the cleaned submissions folder
                shutil.move(str(item), str(extract_to))


        # Remove the now-empty temporary directory
        temp_dir.rmdir()
        
    def unzip_all(self) -> None:
        """
        Unzips all `.zip` files in the submissions directory in parallel using threads.
        """
        # Gather all zip files in the raw submissions directory
        zip_files = list(self.submissions_path.glob("*.zip"))

        # Use ThreadPoolExecutor to unzip multiple submissions concurrently in multiple threads
        with ThreadPoolExecutor() as executor:
            # Submit unzip tasks for each zip file
            futures = [executor.submit(self.unzip, submission) for submission in zip_files]

            # Display progress bar as futures complete
            for _ in tqdm(as_completed(futures), total=len(futures), desc="Unzipping submissions", unit="Submission"):
                pass  

    def remove_unnecessary(self) -> None:
        """
        Removes all files and folders from each submission except those listed in KEEP_FILES.
        """
        if self.cleaned_path.exists():
            # Filter folders that start with "Portfolio" which represent submissions
            folders = [f for f in self.cleaned_path.iterdir() if f.is_dir() and f.name.startswith("Portfolio")]

            # Iterate over each submission folder with a progress bar
            for folder in tqdm(folders, desc="Removing irrelevant files", unit="Submission"):
                # Iterate over all items in the submission folder
                for item in folder.iterdir():
                    # If item is a file and not in the keep list, delete it
                    if item.is_file() and item.name not in self.keep_files:
                        item.unlink()
                    # If item is a directory, remove it entirely
                    elif item.is_dir():
                        shutil.rmtree(item)

    def flatten_directory(self) -> None:
        """
        Moves required files up to the main submission folder level if they are nested in subfolders.
        """
        if self.cleaned_path.exists():
            # Filter submission folders starting with "Portfolio"
            folders = [f for f in self.cleaned_path.iterdir() if f.is_dir() and f.name.startswith("Portfolio")]

            # Iterate over each submission folder with progress bar
            for submission_dir in tqdm(folders, desc="Flattening Folders", unit="Submission"):
                # Iterate over items inside the submission folder
                for subitem in submission_dir.iterdir():
                    if subitem.is_dir():
                        # For directories, check their files and move any keep_files up to submission root
                        for file in subitem.iterdir():
                            if file.is_file() and file.name in self.keep_files:
                                destination = submission_dir / file.name
                                # Move file only if it doesn't already exist at destination
                                if not destination.exists():
                                    file.replace(destination)
                    elif subitem.is_file() and subitem.name in self.keep_files:
                        # File is already at root and should be kept, so continue
                        continue
        else:
            # Inform user if cleaned directory does not exist or was moved
            print("The cleaned directory does not exist or has been moved.")

if __name__ == "__main__":
    folder = CleanSubmission("tests/Non_Cleaned_Test_Files", "Original_Subs")
    # folder.unzip(Path("tests/Non_Cleaned_Test_Files/Portfolio 2 Upload Zone_c444_attempt_2024-04-18-02-19-15_Portfolio2.zip"))
    folder.unzip_all()
    # folder.flatten_directory()
    # folder.remove_unneccesary()