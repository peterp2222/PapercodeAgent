import os
import time

def save_generated_code(task_id, file_info_list, code_dict):
    task_dir = f"generated/{task_id}"
    for file in file_info_list:
        path = file["path"]
        abs_path = os.path.join(task_dir, path)

        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(code_dict[path])
