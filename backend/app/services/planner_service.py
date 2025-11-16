from backend.app.utils.llm_client import call_project_plan_llm

def plan_project(state: dict) -> dict:
    try:
        result = call_project_plan_llm(state["project_description"])

        if "error" in result:
            return {**state, "error": result["error"]}

        file_plan = [
            {
                "path": f["path"],
                "purpose": f["purpose"],
                "dependencies": f.get("dependencies", [])
            }
            for f in result["files"]
        ]

        file_plan.sort(key=lambda x: len(x["dependencies"]))

        return {
            **state,
            "file_plan": file_plan,
            "files_to_process": file_plan.copy()
        }
    except Exception as e:
        return {**state, "error": str(e)}
