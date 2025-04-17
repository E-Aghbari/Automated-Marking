TASK_CONFIG = {
    "Task_1": {
        "test_script": "Testing_1.py",
        "scenario": None,
        "override": []  # No overrides for Task_1
    },
    "Task_2": {
        "test_script": "Testing_2.py",
        "scenario": "Task1_Override",
        "override": ["Task_1.py"]  # Overriding Task_1.py
    },
    "Task_3": {
        "test_script": "Testing_3.py",
        "scenario": "Task1_Task2_Override",
        "override": ["Task_1.py", "Task_2.py"]  # Overriding Task_1.py & Task_2.py
    },
    "Task_4": {
        "test_script": "Testing_4.py",
        "scenario": None,
        "override": []  # No overrides for Task_4
    },
    "Task_5": {
        "test_script": "Testing_5.py",
        "scenario": None,
        "override": []  # No overrides for Task_5
    }
}