from flask import Blueprint, request, jsonify
from backend.app.services.task_manager import (
    start_task,
    get_task_state
)

task_bp = Blueprint("task", __name__)

@task_bp.route('/start-project', methods=['POST'])
def start_project():
    if 'file' not in request.files:
        return {"error": "No file uploaded"}, 400

    pdf = request.files['file']
    task_id, status = start_task(pdf)
    return jsonify({"task_id": task_id, "status": status})

@task_bp.route('/task-status/<task_id>', methods=['GET'])
def task_status(task_id):
    state = get_task_state(task_id)
    if state is None:
        return jsonify({"error": "任务不存在"}), 404
    return jsonify(state)