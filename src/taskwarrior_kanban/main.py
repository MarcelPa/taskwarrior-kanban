import subprocess
import json
import datetime
import os
import sys

# Configs
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
MAX_COMPLETED = 30 # max. no. of completed tasks to display

def get_tasks(tags):

    # run taskwarrior export
    try:
        command = ['task', 'rc.json.depends.array=no', sys.argv[1], 'export'] + tags 
    except:
        command = ['task', 'rc.json.depends.array=no', 'export'] + tags 
    data = subprocess.check_output(command) 
    data = data.decode('utf-8') # decode bytestring to string
    data = data.replace('\n','') # remove newline indicators

    # load taskwarrior export as json data
    tasks = json.loads(data)

    return tasks

def check_due_date(tasks):
    
    for task in tasks:
        if 'due' in task:
            # calculate due date in days
            due_date = datetime.datetime.strptime(task['due'], '%Y%m%dT%H%M%SZ')
            due_in_days = (due_date - datetime.datetime.utcnow()).days
            
            if due_in_days > 7: # if due after a week, remove due date
                task.pop('due', None)
            else:
                task['due'] = due_in_days

def gather_tasks(filters=None):
    """
    Gather and return tasks from taskwarrior.
    
    Filters allows to pass filters for taskwarrior, e.g. to limit the tasks to
    a certain project or specify a timespan. Tasks are returned as a three
    element tuple (todo_tasks, started_tasks, completed_tasks).
    """

    if filters is None:
        filters = []

    # get pending tasks
    pending_tasks = get_tasks(['status:pending'] + filters)

    # get tasks to do
    todo_tasks = [task for task in pending_tasks if 'start' not in task]
    # sort tasks by urgency (descending order)
    todo_tasks = sorted(todo_tasks, key=lambda task: task['urgency'], reverse=True)
    # check due dates
    check_due_date(todo_tasks)

    # get started tasks
    started_tasks = [task for task in pending_tasks if 'start' in task]
    # sort tasks by urgency (descending order)
    started_tasks = sorted(started_tasks, key=lambda task: task['urgency'], reverse=True)
    # check due dates
    check_due_date(started_tasks)

    # get completed tasks and add to master dictionary (same as above)
    completed_tasks = get_tasks(['status:completed'] + filters)[:MAX_COMPLETED]

    return (todo_tasks, started_tasks, completed_tasks)
