#!/usr/bin/env python3

import subprocess
import json
import datetime
import os
import sys
import curses
import pdb

SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))

MAX_COMPLETED = 10 # max. no. of completed tasks to display

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


def render_template(tasks_dic):

    # jinja stuff to load template
    template_loader = jinja2.FileSystemLoader(searchpath=SCRIPT_PATH)
    template_env = jinja2.Environment(loader=template_loader)
    template_file = 'template.jinja'
    template = template_env.get_template(template_file)

    # render template and return html
    return template.render(tasks_dic)    

def write_html(data, filename):

    # write data to file
    with open(filename, 'w') as f:
        f.write(data)

def write_to_window(win, list):
    """
    Writes a list of ToDos to a curses window
    """

    for i, item in enumerate(list):
        # TODO: make fancy word breaking stuff here
        # This one defines the layout
        win.addnstr(i+3, 1,f"{item['description']} [{item['project']}]\n", int(curses.COLS/3)-3)

def main(stdscr):

    # empty master dictionary to be filled up and passed to jinja template rendering function
    tasks_dic = {} 

    # get pending tasks
    pending_tasks = get_tasks(['status:pending'])


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

    # add pending tasks to master dictionary 
    tasks_dic['todo_tasks'] = todo_tasks
    tasks_dic['started_tasks'] = started_tasks

    # get completed tasks and add to master dictionary (same as above)
    completed_tasks = get_tasks(['status:completed']) 
    tasks_dic['completed_tasks'] = completed_tasks[:MAX_COMPLETED]

    #stdscr = curses.initscr()
    curses.start_color()
    curses.noecho()
    curses.cbreak()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_YELLOW)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_GREEN)

    maxwidth = int(curses.COLS/3)
    windows = [None, None, None]
    for win_i in range(0,3):
        windows[win_i] = curses.newwin(curses.LINES, maxwidth-1, 0, win_i * maxwidth)
    stdscr.refresh()
    left, center, right = windows

    left.border(0)
    left.bkgd(' ', curses.color_pair(1))
    left.addstr(1, int(maxwidth/2)-4, "Backlog", curses.A_BOLD)
    left.bkgd(' ', curses.A_NORMAL)
    write_to_window(left, todo_tasks)
    left.refresh()

    center.border(0)
    center.bkgd(' ', curses.color_pair(2))
    center.addstr(1, int(maxwidth/2)-6, "In Progress", curses.A_BOLD)
    center.bkgd(' ', curses.A_NORMAL)
    write_to_window(center, started_tasks)
    center.refresh()

    right.border(0)
    right.bkgd(' ', curses.color_pair(3))
    right.addstr(1, int(maxwidth/2)-3, "Done", curses.A_BOLD)
    right.bkgd(' ', curses.A_NORMAL)
    write_to_window(right, completed_tasks[:min(MAX_COMPLETED, curses.LINES)])
    right.refresh()

    stdscr.getkey()

    curses.nocbreak()
    curses.endwin()

    # pass master dictionary to render template and get html
    #html = render_template(tasks_dic)

    # write html to file
    #write_html(html, SCRIPT_PATH + '/index.html')


if __name__ == '__main__':
    curses.wrapper(main)
