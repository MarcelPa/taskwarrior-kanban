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

def parse_tw_date(datestring):
    """
    Parses the datestring supplied by taskwarrior into a datetime.date object.
    """
    return datetime.datetime.strptime(datestring, '%Y%m%dT%H%M%SZ')

def check_due_date(tasks):
    
    for task in tasks:
        if 'due' in task:
            # calculate due date in days
            date = parse_tw_date(task['due'])
            due_in_days = date - (datetime.datetime.utcnow()).days
            
            if due_in_days > 7: # if due after a week, remove due date
                task.pop('due', None)
            else:
                task['due'] = due_in_days

def check_sched_date(tasks):
    """
    Format the scheduled date in the tasks list.
    """

    for task in tasks:
        if 'scheduled' in task:
            date = parse_tw_date(task['scheduled'])
            
            # check if task in this week
            if date.isocalendar()[1] == (datetime.datetime.utcnow()).isocalendar()[1]:
                task['scheduled'] = date.weekday()
            else:
                task.pop('scheduled', None)

def format_task_details(task):
    """
    Returns a formatted string representation of a tasks details.

    >>> format_task_details({"id":1,"description":"Testtask","due":"20190815T220000Z","entry":"20190809T185715Z","modified":"20190809T185743Z","project":"test","scheduled":"20190812T220000Z","status":"pending","uuid":"66ccc153-318a-4ebf-8ed7-f047cac2b89d","urgency":6.99948})
    '[test]                   due: 2019-08-15     scheduled: 4d'
    """
    if 'project' in task.keys():
        project = f"[{task['project']}]"
    else:
        project = ""
    if 'due' in task.keys():
        due_date = parse_tw_date(task['due'])
        due = f"due: {due_date.date().isoformat()}"
    else:
        due = ""
    if 'scheduled' in task.keys():
        scheduled_date = parse_tw_date(task['scheduled'])
        scheduled = f"scheduled: {scheduled_date - (datetime.datetime.utcnow()).days}d"
    else:
        scheduled = ""
    return f"{project:<50}{due:<20}{scheduled}"


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

    # get started tasks
    started_tasks = [task for task in pending_tasks if 'start' in task]
    # sort tasks by urgency (descending order)
    started_tasks = sorted(started_tasks, key=lambda task: task['urgency'], reverse=True)

    # get completed tasks and add to master dictionary (same as above)
    completed_tasks = get_tasks(['status:completed'] + filters)[:MAX_COMPLETED]

    return (todo_tasks, started_tasks, completed_tasks)
