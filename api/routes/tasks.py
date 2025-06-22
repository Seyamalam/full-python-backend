"""
Task management routes - for demonstrating background processing
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError
import uuid
import datetime
import time
import threading

from api.extensions import db, limiter
from api.models import User

tasks_bp = Blueprint("tasks", __name__)

# In-memory task storage (would use a proper task queue in production)
TASKS = {}

class TaskSchema(Schema):
    """Schema for task data validation"""
    name = fields.String(required=True)
    description = fields.String()
    duration = fields.Integer(required=True, validate=lambda n: 1 <= n <= 60)

def process_task(task_id, duration):
    """Simulate a long-running task"""
    # Update task status to processing
    TASKS[task_id]["status"] = "processing"
    TASKS[task_id]["progress"] = 0
    
    # Simulate processing with progress updates
    steps = 10
    for i in range(steps):
        # Sleep for a portion of the total duration
        time.sleep(duration / steps)
        
        # Update progress
        progress = int((i + 1) / steps * 100)
        TASKS[task_id]["progress"] = progress
        
        # Simulate random failures (5% chance)
        if i == steps - 2 and uuid.uuid4().int % 20 == 0:
            TASKS[task_id]["status"] = "failed"
            TASKS[task_id]["error"] = "Simulated random failure"
            return
    
    # Update task status to completed
    TASKS[task_id]["status"] = "completed"
    TASKS[task_id]["completed_at"] = datetime.datetime.utcnow().isoformat()

@tasks_bp.route("", methods=["POST"])
@jwt_required()
@limiter.limit("10 per minute")
def create_task():
    """
    Create a new background task
    ---
    tags:
      - Tasks
    security:
      - bearerAuth: []
    parameters:
      - in: body
        name: task
        schema:
          type: object
          required:
            - name
            - duration
          properties:
            name:
              type: string
            description:
              type: string
            duration:
              type: integer
              minimum: 1
              maximum: 60
              description: Task duration in seconds (1-60)
    responses:
      201:
        description: Task created successfully
      400:
        description: Validation error
      401:
        description: Unauthorized
    """
    try:
        # Get current user identity
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Validate request data
        schema = TaskSchema()
        data = schema.load(request.json)
        
        # Create task
        task_id = str(uuid.uuid4())
        task = {
            "id": task_id,
            "name": data["name"],
            "description": data.get("description", ""),
            "status": "pending",
            "progress": 0,
            "created_at": datetime.datetime.utcnow().isoformat(),
            "created_by": current_user.username,
            "duration": data["duration"]
        }
        
        # Store task
        TASKS[task_id] = task
        
        # Start background thread to process task
        thread = threading.Thread(
            target=process_task,
            args=(task_id, data["duration"])
        )
        thread.daemon = True
        thread.start()
        
        # Return task details
        return jsonify({
            "message": "Task created successfully",
            "task": task
        }), 201
        
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tasks_bp.route("", methods=["GET"])
@jwt_required()
def get_tasks():
    """
    Get all tasks for current user
    ---
    tags:
      - Tasks
    security:
      - bearerAuth: []
    responses:
      200:
        description: List of tasks
      401:
        description: Unauthorized
    """
    try:
        # Get current user identity
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Filter tasks by username (or return all for admin)
        if current_user.role == "admin":
            tasks = list(TASKS.values())
        else:
            tasks = [task for task in TASKS.values() if task.get("created_by") == current_user.username]
        
        # Sort tasks by created_at desc
        tasks.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        # Return tasks
        return jsonify({
            "tasks": tasks
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tasks_bp.route("/<task_id>", methods=["GET"])
@jwt_required()
def get_task(task_id):
    """
    Get task by ID
    ---
    tags:
      - Tasks
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: task_id
        schema:
          type: string
        required: true
    responses:
      200:
        description: Task details
      401:
        description: Unauthorized
      403:
        description: Forbidden - Not allowed to access this task
      404:
        description: Task not found
    """
    try:
        # Check if task exists
        if task_id not in TASKS:
            return jsonify({"error": "Task not found"}), 404
        
        # Get task
        task = TASKS[task_id]
        
        # Get current user identity
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Check if current user is admin or the task creator
        if current_user.role != "admin" and task.get("created_by") != current_user.username:
            return jsonify({"error": "Not authorized to access this task"}), 403
        
        # Return task details
        return jsonify({
            "task": task
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@tasks_bp.route("/<task_id>/cancel", methods=["POST"])
@jwt_required()
def cancel_task(task_id):
    """
    Cancel a pending or processing task
    ---
    tags:
      - Tasks
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: task_id
        schema:
          type: string
        required: true
    responses:
      200:
        description: Task cancelled successfully
      400:
        description: Task cannot be cancelled
      401:
        description: Unauthorized
      403:
        description: Forbidden - Not allowed to cancel this task
      404:
        description: Task not found
    """
    try:
        # Check if task exists
        if task_id not in TASKS:
            return jsonify({"error": "Task not found"}), 404
        
        # Get task
        task = TASKS[task_id]
        
        # Get current user identity
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Check if current user is admin or the task creator
        if current_user.role != "admin" and task.get("created_by") != current_user.username:
            return jsonify({"error": "Not authorized to cancel this task"}), 403
        
        # Check if task can be cancelled
        if task["status"] not in ["pending", "processing"]:
            return jsonify({"error": f"Task cannot be cancelled (status: {task['status']})"}), 400
        
        # Cancel task
        task["status"] = "cancelled"
        
        # Return task details
        return jsonify({
            "message": "Task cancelled successfully",
            "task": task
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500