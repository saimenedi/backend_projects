import argparse
import json
import sys
import os
from datetime import datetime

#Configuration
DATA_FILE = "tasks.json"

def load_tasks():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("Error: tasks.json is corrupted.")
        return []

def save_tasks(tasks):
    try: 
        with open(DATA_FILE, 'w') as f:
            json.dump(tasks, f, indent=4)
        return True
    except IOError as e:
        print(f"Error saving tasks: {e}")
        return False

def get_next_id(tasks):
    if not tasks:
        return 1
    return max(task['id'] for task in tasks) + 1

def add_task(description, tasks):
    new_task = {
        "id": get_next_id(tasks),
        "description": description,
        "status": "todo",
        "created_at": datetime.now().isoformat()
    }
    tasks.append(new_task)
    if save_tasks(tasks):
        print(f"Task added sucessfully with ID: {new_task['id']}")

def update_task(task_id, new_description, tasks):
    for task in tasks:
        if task['id'] == task_id:
            task['description'] = new_description
            if save_tasks(tasks):
                print(f"Task {task_id} updated.")
            return
    print(f"Error: Task with ID {task_id} not found.")

def delete_task(task_id, tasks):
    for i, task in enumerate(tasks):
        if task['id'] == task_id:
            removed = tasks.pop(i)
            if save_tasks(tasks):
                print(f"Task {task_id} deleted: '{removed['description']}'")
            return
    print(f"Error: Task with ID {task_id} not found.")

def mark_task(task_id, status, tasks):
    valid_statuses = ['in_progress', 'done']
    if status not in valid_statuses:
        print("Error: Invalid status. Choose from {valid_statuses}.")
        return

    for task in tasks:
        if task['id'] == task_id:
            old_status = task['status']
            task['status'] = status
            if save_tasks(tasks):
                print(f"Task {task_id} marked as '{status}'.")
            return
    print(f"Error: Task with ID {task_id} not found.")

def list_tasks(status_filter = None, tasks = None):
    if not tasks:
        tasks = load_tasks()

    if not tasks:
        print("No tasks found.")
        return

    filtered_tasks = tasks
    if status_filter:
        filtered_tasks = [t for t in tasks if t['status'] == status_filter]

        if not filtered_tasks:
            status_msg = f"({status_filter})" if status_filter else print(f"No tasks found {status_msg}.")
            return
    print(f"\n{'ID':<5} {'Status':<15} {'Description'}")
    print("-" * 40)
    for task in filtered_tasks:
        print(f"{task['id']:<5} {task['status']:<15} {task['description']}")
    print()
def main():
    parser = argparse.ArgumentParser(description="Task Tracker CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # 1. Add Task
    parser_add = subparsers.add_parser("add", help="Add a new task")
    parser_add.add_argument("description", type=str, help="Task description")

    # 2. Update Task
    parser_update = subparsers.add_parser("update", help="Update a task description")
    parser_update.add_argument("id", type=int, help="Task ID to update")
    parser_update.add_argument("description", type=str, help="New description")

    # 3. Delete Task
    parser_delete = subparsers.add_parser("delete", help="Delete a task")
    parser_delete.add_argument("id", type=int, help="Task ID to delete")

    # 4. Mark Task
    parser_mark = subparsers.add_parser("mark", help="Mark task as in_progress or done")
    parser_mark.add_argument("id", type=int, help="Task ID to mark")
    parser_mark.add_argument("status", type=str, choices=["in_progress", "done"], help="New status")

    # 5. List Tasks
    parser_list = subparsers.add_parser("list", help="List tasks")
    parser_list.add_argument("--filter", dest="filter", type=str, 
                             choices=["todo", "in_progress", "done", "all"], 
                             help="Filter by status")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    tasks = load_tasks()

    if args.command == "add":
        add_task(args.description, tasks)
    elif args.command == "update":
        update_task(args.id, args.description, tasks)
    elif args.command == "delete":
        delete_task(args.id, tasks)
    elif args.command == "mark":
        mark_task(args.id, args.status, tasks)
    elif args.command == "list":
        # Map 'all' to None to show everything, otherwise use the filter
        status = args.filter if args.filter != "all" else None
        list_tasks(status_filter=status, tasks=tasks)

if __name__ == "__main__":
    main()
