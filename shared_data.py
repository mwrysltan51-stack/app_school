import json
import os
DATA_FILE = "data.json"
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "teacher_name": "",
        "teacher_pass": "",
        "subject_name": "اسم المادة",
        "classes_structure": {}
    }
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)