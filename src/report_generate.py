"""
Report Generation Module for Automated Marking System

This module includes functionality to:
- Parse test logs and extract test case results.
- Generate detailed task-level reports with student-wise test outputs.
- Generate a detailed setup-level report indicating virtual environment setup outcomes.
"""
import pandas as pd
from pathlib import Path
import re
from collections import defaultdict

def parse_log(task: str, log_path: str | Path) -> list:
    """
    Parses the test log for a specific task and extracts test case results.

    Args:
        task (str): Task identifier (e.g., 'Task_1').
        log_path (str or Path): Path to the test log file.

    Returns:
        list: A list of dictionaries containing test name, input, expected output, actual output, and result status.
    """
    test_cases = []

    # Parse logs based on certain task
    pattern = {
        "Task_1": re.compile(r"(?P<test_name>[\w\s;]+);Correct (?P<status>True|False)\*+\n(?:.*?; on input (?P<input>\[[^\]]*\]|\{[^\}]*\}|[^\s\n]+)\.?)?(?: and similarity (True|False)\.)?(?:;?\s*Expected\s+(?P<expected>\[[\s\S]*?\]|\{[\s\S]*?\}|.*?)\sand got\s(?P<got>\[[\s\S]*?\]|\{[\s\S]*?\}|.*?))(?=\nDEBUG:root|$)",
        re.DOTALL
    ),

        "Task_2": re.compile(r"^DEBUG:root:(?P<test_name>.+?);Correct (?P<status>True|False)\*+\s*\n;(?:.*?; on input (?P<input>\[[^\]]*\]|\{[^\}]*\}|[^\s\n]+)\.?)? got (?P<got>[\s\S]*?) and expected (?P<expected>[\s\S]*?)(?=\nDEBUG:root:|\Z)",
        re.MULTILINE
    ),
        "Task_3": re.compile(r"^DEBUG:root:(?P<test_name>.+?);Correct (?P<status>True|False)(?:.*?; on input (?P<input>\[[^\]]*\]|\{[^\}]*\}|[^\s\n]+)\.?)?(?:;\s*(?P<inline_got>.*?))?\*+\s*(?:;\s*Expected\s*(?P<expected>[\s\S]*?)\s*and got\s*(?P<got>[\s\S]*?))?(?=\nDEBUG:root:|\Z)",
        re.MULTILINE
    ),
        "Task_4": re.compile(r"DEBUG:root:(?P<test_name>[^\n;]+);Correct (?P<status>True|False)\*+\n(?:; on input (?P<input>.*?)\.\s*)?(?:;?\s*Staff produced (?P<expected>[\d\.]+) and student produced (?P<got>[\d\.]+))?(?:;?\s*(?!on input)(?P<got_fallback>.+?))?(?=\nDEBUG:root:|\Z)",
        re.DOTALL
    )
    }

    with open(log_path, 'r', encoding='utf-8') as f:
        log_content = f.read()  # Read entire file for multi-line matches
    
    # Extract test cases results using regular expressions
    blocks = re.split(r'(?=DEBUG:root:)', log_content.strip())
    

    for block in blocks:
        match = pattern[task].search(block)
        if match:
            test_name = match.group("test_name").strip()
            status = 'Passed' if match.group("status") == 'True' else 'Failed'
            test_input = (match.group("input").strip() if "input" in match.re.groupindex and match.group("input") else "No Input")
            expected = match.group("expected").strip() if "expected" in match.re.groupindex and match.group("expected") else "N/A"
            got = (
            (match.group("got").strip() if "got" in match.re.groupindex and match.group("got") else None)
            or (match.group("got_fallback").strip() if "got_fallback" in match.re.groupindex and match.group("got_fallback") else None)
            or "N/A"
        )

            test_cases.append({
                'Test Name': test_name,
                'Input': test_input,
                'Status': status,
                'Expected': expected,
                'Got': got.strip() if isinstance(got, str) else got
            })

    return test_cases

def generate_detailed_report(task: str, submissions_root: Path) -> None:
    """
    Generates a detailed Excel report showing test case results for each student for a given task.

    Args:
        task (str): Task identifier (e.g., 'Task_1').
        submissions_root (strPath): Directory containing cleaned student submission folders.
    """

    # Extract task number and configuration
    task_number = task.split('_')[1]
    crash_texts = {}
    test_cases = {}
    missing_students = []

    # Iterate through student directories and filter based on scenario
    for student_dir in submissions_root.iterdir():
        if not student_dir.is_dir():
            continue

        if not student_dir.name.startswith("Portfolio"):
            continue

        student_name = student_dir.name
        report_data = []
            
        log_file = student_dir / f"test_{task_number}.log"

        match = re.search(r"[cC]\d{2,}", student_name)

        if match:
            student_ID = match.group(0)
        

        # Check if log file exists and parse it
        if log_file.exists():
            try:
                # Parse the log file for test cases and results
                cases = parse_log(task, log_file)
                for case in cases:
                    test_name = case["Test Name"]
                    input_params = case["Input"]
                    expected = case['Expected']
                    result = case["Status"]
                    actual = case['Got']

                    test_key = (test_name, str(input_params)) 

                    if test_key not in test_cases:
                        # Initialize test case entry with expected output and test details
                        test_cases[test_key] = {
                            "Test Name": test_name,
                            "Input Parameters": input_params,
                            "Expected Output": expected
                        }
                    else:
                    #     # 🧠 If expected output is better than the current 'N/A', update it
                        if test_cases[test_key]["Expected Output"] == "N/A" and expected != "N/A":
                            test_cases[test_key]["Expected Output"] = expected
                    

                    # Add student's output and result keyed by student ID or name
                    test_cases[test_key][f"{student_ID if student_ID else student_name} - Output"] = actual
                    test_cases[test_key][f"{student_ID if student_ID else student_name} - Result"] = result

            except Exception as e:
                # Handle parsing errors by logging an error entry for the student
                test_cases[f"{student_ID if student_ID else student_name}_ERROR"] = {
                    "Test Name": "PARSE ERROR",
                    "Input Parameters": str(e),
                    "Expected Output": "",
                    f"{student_ID if student_ID else student_name} - Output": "",
                    f"{student_ID if student_ID else student_name} - Result": "Error"
                }
        else:
            # Track students missing their log files
            missing_students.append(student_ID if student_ID else student_name)


        # Handle missing or crashed test cases
        crash_file = student_dir / f"TEST_{task}.crash"
        has_crashed = crash_file.exists()
        crash_text = ""

        if has_crashed:
            try:
                crash_text = crash_file.read_text(encoding= 'utf-8').strip()
            except Exception as e:
                crash_text = f" Failed to read crash file: {e}"
            crash_texts[student_ID if student_ID else student_name] = crash_text

        for test_key in list(test_cases.keys()):
            output_key = f"{student_ID if student_ID else student_name} - Output"
            result_key = f"{student_ID if student_ID else student_name} - Result"

            if output_key not in test_cases[test_key]:
                if has_crashed:
                    test_cases[test_key][output_key] = "Test Crashed"
                    test_cases[test_key][result_key] = crash_text or "Crashed"
                elif student_name in missing_students:
                    test_cases[test_key][output_key] = "Missing Log"
                    test_cases[test_key][result_key] =  "Missing Log"
                else:
                    test_cases[test_key][output_key] = "Not Available"
                    test_cases[test_key][result_key] = "Not Ran"

    # If no test cases were detected, add a placeholder entry
    # to indicate that no tests were run
    if not test_cases:
        test_cases[("No Test Cases Detected", "")] = {
            "Test Name": "No Test Cases Detected",
            "Input Parameters": "",
            "Expected Output": ""
        }

    # For students missing logs entirely, fill all test rows with missing log info
    for test_row in test_cases.values():
        for student in missing_students:
            student_crash = crash_texts.get(student, None)
            test_row[f"{student} - Output"] = "Missing Log"
            test_row[f"{student} - Result"] = student_crash or  "Missing Log"


    # Create DataFrame from test cases and save as Excel report
    report_data = list(test_cases.values())
    df = pd.DataFrame(report_data)
    df.fillna("Not Ran", inplace=True)

    # Save consolidated report to Excel file
    task_report = submissions_root / f"{task}_Consolidated_Report.xlsx"
    df.to_excel(task_report, index=False)
    print(f"Generated {task} consolidated report: {task_report}")


def generate_setup_report(submissions: Path) -> None:
    """
    Generates a summary report of virtual environment setup logs from each student directory.

    Args:
        submissions (Path): Directory containing student folders with 'log.txt' setup logs.
    """
    # Initialise data storage for methods and results
    data = defaultdict(dict)
    student_names = set()

    # Iterate through student directories and filter based on scenario
    for submission in submissions.iterdir():

        if not submission.is_dir():
            continue

        log_file = submission / "log.txt"

        if not log_file.exists():
            continue

        student_name = submission.name

        match = re.search(r"[cC]\d{4,}", student_name)
        if match:
            student_name = match.group(0)

        student_names.add(student_name)

        # Read each line of the setup log and extract method, result, and message
        with open(log_file, 'r') as log:
            for line in log:
                line = line.strip()
                match = re.match(r"^(.*?); (.*?): (.*)$", line)
                if not match:
                    continue
                (method, result, message) = match.groups()
                data[method][student_name] = (result, message)
    
    rows = []

    # Construct rows for each test case and student with results and messages
    for method in data.keys():
        row = {"Test case": method}
        for student in student_names:
            if student in data[method]:
                result, message = data[method][student]

            else:
                result, message = "MISSING", "No log entry"
            row[f"{student} - Result"] = result
            row[f"{student} - Message"] = message
        rows.append(row)

    # Create DataFrame and export to Excel
    df = pd.DataFrame(rows)
    # Export the setup report to Excel
    task_report = submissions / "Students_Preparation_Report.xlsx"
    df.to_excel(task_report, index=False)

    print(f"Collated report for preparation has been created in {task_report}")

if __name__ == "__main__":
    pass