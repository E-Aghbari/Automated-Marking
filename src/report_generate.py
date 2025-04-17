import pandas as pd
from pathlib import Path
import re
from config import TASK_CONFIG
from collections import defaultdict

def parse_log(task, log_path):
    test_cases = []

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

def generate_detailed_report(task, submissions_root: Path):
    task_number = task.split('_')[1]
    config = TASK_CONFIG.get(task)
    all_reports = []
    test_cases = {}
    missing_students = []
    
    for student_dir in submissions_root.iterdir():
        if not student_dir.is_dir():
            continue

        if not student_dir.name.startswith("Portfolio"):
            continue

        student_name = student_dir.name
        report_data = []

        # If scenario is None, ensure submission is the original (no override in name)
        if config["scenario"] is None:
            if any(scenario["scenario"] in student_dir.name for scenario in TASK_CONFIG.values() if scenario["scenario"]):
                continue  # Skip if it's an override folder
        else:
            # If scenario exists, ensure it matches submission name
            if config["scenario"] not in student_dir.name:
                continue
        
        # Determine correct log path based on task scenario
        if config["scenario"]:
            log_path = student_dir.parent / f"{student_name}"
        else:
            log_path = student_dir
            
        log_file = log_path / f"test_{task_number}.log"

        match = re.search(r"[cC]\d{4,}", student_name)

        if match:
            student_ID = match.group(0)
        


        if log_file.exists():
            try:
                cases = parse_log(task, log_file)
                for case in cases:
                    test_name = case["Test Name"]
                    input_params = case["Input"]
                    expected = case['Expected']
                    result = case["Status"]
                    actual = case['Got']

                    test_key = (test_name, str(input_params)) 

                    if test_key not in test_cases:
                        test_cases[test_key] = {
                            "Test Name": test_name,
                            "Input Parameters": input_params,
                            "Expected Output": expected
                        }
                    else:
                    #     # 🧠 If expected output is better than the current 'N/A', update it
                        if test_cases[test_key]["Expected Output"] == "N/A" and expected != "N/A":
                            test_cases[test_key]["Expected Output"] = expected
                    

                    # Add student's output and result
                    test_cases[test_key][f"{student_ID if student_ID else student_name} - Output"] = actual
                    test_cases[test_key][f"{student_ID if student_ID else student_name} - Result"] = result

            except Exception as e:
                test_cases[f"{student_ID if student_ID else student_name}_ERROR"] = {
                    "Test Name": "PARSE ERROR",
                    "Input Parameters": str(e),
                    "Expected Output": "",
                    f"{student_ID if student_ID else student_name} - Output": "",
                    f"{student_ID if student_ID else student_name} - Result": "Error"
                }

        else:
            missing_students.append(student_ID if student_ID else student_name)


        # ✅ HERE: detect and process crashed/missing tests
        crash_file = log_path / f"TEST_{task}.crash"
        has_crashed = crash_file.exists()

        for test_key in list(test_cases.keys()):
            output_key = f"{student_ID if student_ID else student_name} - Output"
            result_key = f"{student_ID if student_ID else student_name} - Result"
            if output_key not in test_cases[test_key]:
                if has_crashed:
                    test_cases[test_key][output_key] = "Test Crashed"
                    test_cases[test_key][result_key] = "Crashed"
                elif student_name in missing_students:
                    test_cases[test_key][output_key] = "Missing Log"
                    test_cases[test_key][result_key] = "Missing Log"
                else:
                    test_cases[test_key][output_key] = "Not Available"
                    test_cases[test_key][result_key] = "Not Ran"

    for test_row in test_cases.values():
        for student in missing_students:
            test_row[f"{student} - Output"] = "Missing Log"
            test_row[f"{student} - Result"] = "Missing Log"


    # Convert to DataFrame
    report_data = list(test_cases.values())
    df = pd.DataFrame(report_data)
    print(df)
    df.fillna("Not Ran", inplace=True)
    # Save consolidated report
    task_report = submissions_root / f"{task}_Consolidated_Report.xlsx"
    df.to_excel(task_report, index=False)
    print(f"✅ Generated {task} consolidated report: {task_report}")
    #         try:
    #             cases = parse_log(log_file)
    #             for case in cases:
    #                 report_data.append({
    #                     'Test name': case['Test Name'],
    #                     'Input Parameters': case['Input'],
    #                     'Expected': case['Test Name'],
    #                     f'{student_name} Result': case['Status'],
    #                     f'{student_name} Got': case['Got']
    #                 })

    #                 report_data.append({
    #                     'Student': student_name,
    #                     'Task': task,
    #                     'Test Name': case['Test Name'],
    #                     'Input Parameters': case['Input'],
    #                     'Result': case['Status']
    #                 })
    #         except Exception as e:
    #             report_data.append({
    #                 'Student': student_name,
    #                 'Task': task,
    #                 'Test Name': 'PARSE ERROR',
    #                 'Input Parameters': str(e),
    #                 'Result': 'Error'
    #             })
    #     else:
    #         report_data.append({
    #             'Student': student_name,
    #             'Task': task,
    #             'Test Name': 'MISSING LOG',
    #             'Input Parameters': '',
    #             'Result': 'Not Executed'
    #         })

    #     # Save individual student report
    #     student_df = pd.DataFrame(report_data)
    #     student_report = submissions_root / f"{student_name}_{task}_Report.xlsx"
    #     student_df.to_excel(student_report, index=False)
        
    #     all_reports.extend(report_data)

    # # Generate consolidated task report
    # task_df = pd.DataFrame(all_reports)
    # task_report = submissions_root / f"{task}_Consolidated_Report.xlsx"
    # task_df.to_excel(task_report, index=False)
    # print(f"Generated {task} consolidated report: {task_report}")

    #///////////////////////////////////////////////////////////////

    # Update accumulated report
    # accumulated_report = submissions_root / "Accumulated_Report.xlsx"
    # try:
    #     existing_df = pd.read_excel(accumulated_report)
    #     combined_df = pd.concat([existing_df, task_df], ignore_index=True)
    # except FileNotFoundError:
    #     combined_df = task_df
        
    # combined_df.to_excel(accumulated_report, index=False)
    # print(f"Updated accumulated report: {accumulated_report}")

def generate_setup_report(submissions: Path):
    data = defaultdict(dict)
    student_names = set()

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

        
        
        with open(log_file, 'r') as log:
            for line in log:
                line = line.strip()
                match = re.match(r"^(.*?); (.*?): (.*)$", line)
                if not match:
                    continue
                (method, result, message) = match.groups()
                data[method][student_name] = (result, message)
    
    rows = []

    for method in data.keys():
        row = {"Test case": method}
        for student in student_names:
            if student in data[method]:
                result, message = data[method][student]
                # row[f"{student} - Result"] = result
                # row[f"{student} - Message"] = message
            else:
                result, message = "MISSING", "No log entry"
            row[f"{student} - Result"] = result
            row[f"{student} - Message"] = message
        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_excel("Students_preparation_report.xlsx", index=False)

    print("Student collated report for preparatoin is done.")





        


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description="Generate detailed test case reports")
    # parser.add_argument("--task", type=int, required=True, help="Task number to analyze")
    # args = parser.parse_args()
    # generate_detailed_report(args.task)

    generate_detailed_report("Task_1",Path("tests/Cleaned_Test_Files"))
    # results = parse_log('Task_1','test_1.log')

    # for case in results:
    #     print("🔍 Test Case")
    #     print(f"Name     : {case['Test Name']}")
    #     print(f"Status   : {case['Status']}")
    #     print(f"Input    : {case['Input']}")
    #     print(f"Expected : {case['Expected']}")
    #     print(f"Got      : {case['Got']}")
    #     print("-" * 50)