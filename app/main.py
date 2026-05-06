"""
Secure Task Manager REST API
Features:
  1. Task creation with input validation
  2. Task listing with filtering
  3. Task deletion with authorization check
"""

import logging
import os
import re
from flask import Flask, jsonify, request

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log"),
    ],
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

tasks: dict = {}
_next_id = 1


def _validate_title(title):
    if not title or not isinstance(title, str):
        return "title is required and must be a string"
    title = title.strip()
    if len(title) > 200:
        return "title must be 200 characters or fewer"
    if re.search(r"[<>\"'`]", title):
        return "title contains disallowed characters"
    return None


@app.route("/health", methods=["GET"])
def health():
    logger.info("Health check requested")
    return jsonify({"status": "ok"}), 200


@app.route("/tasks", methods=["GET"])
def list_tasks():
    done_filter = request.args.get("done")
    if done_filter is not None:
        done_bool = done_filter.lower() == "true"
        result = [t for t in tasks.values() if t["done"] == done_bool]
    else:
        result = list(tasks.values())
    logger.info("Listed %d task(s)", len(result))
    return jsonify(result), 200


@app.route("/tasks", methods=["POST"])
def create_task():
    global _next_id
    data = request.get_json(silent=True) or {}
    title = data.get("title", "")

    err = _validate_title(title)
    if err:
        logger.warning("Task creation failed: %s", err)
        return jsonify({"error": err}), 400

    task = {"id": _next_id, "title": title.strip(), "done": False}
    tasks[_next_id] = task
    logger.info("Created task id=%d title=%r", _next_id, title)
    _next_id += 1
    return jsonify(task), 201


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    role = request.headers.get("X-User-Role", "guest")
    if role != "admin":
        logger.warning("Unauthorized delete attempt for task id=%d", task_id)
        return jsonify({"error": "forbidden - admin role required"}), 403

    if task_id not in tasks:
        logger.warning("Delete: task id=%d not found", task_id)
        return jsonify({"error": "task not found"}), 404

    del tasks[task_id]
    logger.info("Deleted task id=%d", task_id)
    return jsonify({"message": f"task {task_id} deleted"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    logger.info("Starting Task Manager API on port %d", port)
    # nosec B104 — binding to all interfaces is intentional for containerised deployment;
    # access is restricted at the network/firewall level in production.
    app.run(host="0.0.0.0", port=port, debug=False)  # nosec B104