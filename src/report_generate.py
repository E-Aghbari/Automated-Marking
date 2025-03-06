import argparse
import pandas as pd
from pathlib import Path
import re

def parse_log(log_path):
    test_cases = []
    pattern = re.compile(
        r'DEBUG:root:(.*?);Correct (True|False)\*+.*?; on input (.*?)\.',
        re.DOTALL
    )
    
    with open(log_path, 'r') as f:
        for line in f:
            match = pattern.search(line)
            if match:
                test_name = match.group(1).strip()
                status = 'Passed' if match.group(2) == 'True' else 'Failed'
                test_input = match.group(3).strip()
                
                test_cases.append({
                    'Test Name': test_name,
                    'Input': test_input,
                    'Status': status
                })
    
    return test_cases

def generate_detailed_report(task_number, submissions_dir="submissions"):
    report_data = []
    
    for student_dir in Path(submissions_dir).iterdir():
        if not student_dir.is_dir():
            continue
        
        student_name = student_dir.name
        log_file = student_dir / f"Test_{task_number}.log"
        
        if log_file.exists():
            try:
                cases = parse_log(log_file)
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
    report_name = f"Task_{task_number}_Detailed_Report.xlsx"
    
    # Formatting for readability
    df = df[['Student', 'Task', 'Test Name', 'Input Parameters', 'Result']]
    df.to_excel(report_name, index=False)
    print(f"Generated detailed report: {report_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate detailed test case reports")
    parser.add_argument("--task", type=int, required=True, help="Task number to analyze")
    args = parser.parse_args()
    generate_detailed_report(args.task)