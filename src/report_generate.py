import argparse
import pandas as pd
from pathlib import Path
import re
from test_manager import TASK_CONFIG

def parse_log(log_path):
    test_cases = []
    pattern = re.compile(
        r'DEBUG:root:([^\n;]+);Correct (True|False)\*+(?:.*?; on input ((?:\[[^\]]*\]|\{[^\}]*\}|[^\n]+)))?',
        re.DOTALL
    )
    
    with open(log_path, 'r') as f:
        log_content = f.read()  # Read entire file for multi-line matches
    
    matches = pattern.findall(log_content)
    print(matches)
    
    for match in matches:
        test_name = match[0].strip()
        status = 'Passed' if match[1] == 'True' else 'Failed'
        test_input = match[2].strip() if match[2] else "No input"

        test_cases.append({
            'Test Name': test_name,
            'Input': test_input,
            'Status': status
        })

    return test_cases

def generate_detailed_report(task, student_dir):
    report_data = []

    student_path = Path(student_dir)
    if not student_path.is_dir() :
        print(f"Skipping invalid directory: {student_dir}")
        return

    student_name = student_path.name
    task_number = int(task[-1])
    log_file = student_path / TASK_CONFIG[task]["scenario"] / f"Test_{task_number}.log"

    if log_file.exists():
        try:
            cases = parse_log(log_file)
            # print(cases)
            for case in cases:
                report_data.append({
                    'Student': student_name,
                    'Task': f'Task_{task_number}',
                    'Test Name': case['Test Name'],
                    'Input Parameters': case['Input'],
                    'Result': case['Status']
                })
        except Exception as e:
            report_data.append({
                'Student': student_name,
                'Task': f'Task_{task_number}',
                'Test Name': 'PARSE ERROR',
                'Input Parameters': str(e),
                'Result': 'Error'
            })
    else:
        report_data.append({
            'Student': student_name,
            'Task': f'Task_{task_number}',
            'Test Name': 'MISSING LOG',
            'Input Parameters': '',
            'Result': 'Not Executed'
        })

    df = pd.DataFrame(report_data)
    report_name = student_dir / f"{student_name}_Task_{task_number}_Report.xlsx"

    # Formatting for readability
    df = df[['Student', 'Task', 'Test Name', 'Input Parameters', 'Result']]
    df.to_excel(report_name, index=False)
    print(f"Generated detailed report: {report_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate detailed test case reports")
    parser.add_argument("--task", type=int, required=True, help="Task number to analyze")
    args = parser.parse_args()
    generate_detailed_report(args.task)