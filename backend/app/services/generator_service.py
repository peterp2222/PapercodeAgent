import time
from backend.app.utils.llm_client import call_generate_code_llm, call_api_summary_llm
from backend.app.utils.file_io import save_generated_code
from backend.app.services.base import CodeGenerationState


def select_next_file(state: CodeGenerationState) -> CodeGenerationState:
    """选择下一个要生成的文件"""
    remaining_files = [
        f for f in state["file_plan"]
        if f["path"] not in state["completed_files"]
    ]

    available_files = [
        f for f in remaining_files
        if all(dep in state["completed_files"] for dep in f["dependencies"])
    ]

    state["current_file"] = available_files
    return state
def process_api_summary(state: dict) -> dict:
    """处理API摘要并更新状态"""
    if not state.get("generated_code") or not state.get("current_file"):
        return {**state, "error": "缺少生成的代码或当前文件"}

    try:
        # 保存文件到完成列表
        completed_files = []
        # 遍历 current_file 与 generated_code，对应生成完成文件
        for cur_file, gen_code in zip(state["current_file"], state["generated_code"]):
            completed_files.append(cur_file.get("path"))

        updated_completed = state.get("completed_files", []) + completed_files

        # （可选）提取API摘要
        api_summary = call_api_summary_llm(state)
        # updated_api_summaries = {**state["api_summaries"], state["current_file"]["path"]: api_summary}
        state["api_summaries"].extend(api_summary)

        return {
            **state,
            "completed_files": updated_completed,
            "generated_code": None,  # 重置
            "current_file": None  # 重置
        }
    except Exception as e:
        return {**state, "error": f"处理API摘要失败: {str(e)}"}

def execute_full_generation(task_id):
    from backend.app.services.task_manager import TASK_STATES
    state = TASK_STATES[task_id]

    state["status"] = "generating"

    try:
        while state["files_to_process"] and not state.get("error"):
            next_files = select_next_file(state)
            if len(next_files["current_file"]) == 0:
                break
            generated = call_generate_code_llm(next_files)
            save_generated_code(task_id, generated["current_file"], generated["generated_code"])
            processed = process_api_summary(generated)

            state.update(processed)
            state["progress"] = len(state["completed_files"]) / state["total_files"] * 100

            TASK_STATES[task_id] = state

        state["status"] = "completed" if not state.get("error") else "error"
        state["actual_time"] = int(time.time() - state["start_time"])
        TASK_STATES[task_id] = state

    except Exception as e:
        state["error"] = str(e)
        state["status"] = "error"
        TASK_STATES[task_id] = state
