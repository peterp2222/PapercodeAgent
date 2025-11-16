import threading
import time
import os
from backend.app.services.planner_service import plan_project
from backend.app.services.generator_service import execute_full_generation
from backend.app.utils.llm_client import call_pdf_reader_llm

TASK_STATES = {}

def init_task_state(project_description):
    return {
        "project_description": project_description,
        "file_plan": [],
        "completed_files": [],
        "api_summaries": [],
        "current_file": None,
        "generated_code": None,
        "files_to_process": [],
        "error": None,
        "total_files": 0,
        "progress": 0,
        "status": "planning",
        "start_time": time.time(),
    }

def start_task(pdf_file):
    images_info = ""
    project_description = call_pdf_reader_llm(pdf_file, images_info)

    task_id = f"task_{int(time.time())}_{os.urandom(4).hex()}"
    TASK_STATES[task_id] = init_task_state(project_description)

    threading.Thread(target=execute_plan_thread, args=(task_id,), daemon=True).start()
    return task_id, "planning"

def execute_plan_thread(task_id):
    try:
        state = TASK_STATES[task_id]
        result = plan_project(state)

        if result["error"]:
            state["error"] = result["error"]
            state["status"] = "error"
        else:
            state.update(result)
            state["total_files"] = len(result["file_plan"])

            threading.Thread(
                target=execute_full_generation,
                args=(task_id,),
                daemon=True
            ).start()

        TASK_STATES[task_id] = state

    except Exception as e:
        TASK_STATES[task_id]["error"] = str(e)
        TASK_STATES[task_id]["status"] = "error"

def get_task_state(task_id):
    return TASK_STATES.get(task_id)
