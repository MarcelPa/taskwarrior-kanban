#!/usr/bin/env python3

import subprocess
import json
import datetime
import os
import sys
import curses
# TODO: remove after development
import pdb

# Configs
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
MAX_COMPLETED = 30 # max. no. of completed tasks to display
CONTROLS_LINES = 7 # number of lines that will be used by the 'controls' field
BORDER_CELLS = 1 # number of cells that will be used to pad the colums on the left and right

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


def write_to_window(win, list, attr=curses.A_NORMAL):
    """
    Writes a list of ToDos to a curses window
    """
    win_height, win_width = win.getmaxyx()

    # if the list is longer than the maximum height, truncate it TODO: make something smarter here (scrolling?)
    if len(list) > win_height:
        list = list[:win_height-1]

    # for readibility, each second line shall have a black backound
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    colorize = (curses.A_NORMAL, curses.color_pair(1))

    # iterate through all ToDos within the list
    for i, item in enumerate(list):
        # This one defines the layout
        desc = f"{item['description']} [{item['project']}]"
        # Truncate the description if too long
        if len(desc) > win_width - BORDER_CELLS*2:
            # maximum length: window    - border         - length of project title - (space and square bracket chars ( = 3)) - (three dots)
            max_desc_length = win_width - BORDER_CELLS*2 - len(item['project']) - 3 - 3
            desc = f"{item['description'][:max_desc_length]}... [{item['project']}]"
        # If not long enough, pad with spaces in order to pain a whole line
        else:
            desc = f"{desc}{' ' * (win_width - BORDER_CELLS*2 - len(desc))}"
        

        # Write description to the window
        win.addstr(i+3, 2,f"{desc}", colorize[i%2] | attr)

def write_windowtitle(win, title):
    """ 
    Writes a title to window such that it is centered in the first line of a window.
    """

    win_width = win.getmaxyx()[1]
    if len(title) > win_width:
        title = f"{title[:win_width-3]}..."
    win.addstr(1, int(win_width/2 - len(title)/2), title, curses.A_BOLD)

def main(stdscr):

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

    # get completed tasks and add to master dictionary (same as above)
    completed_tasks = get_tasks(['status:completed'])[:min(curses.LINES, MAX_COMPLETED)]

    #stdscr = curses.initscr()
    MAX_WIN_WIDTH = int(curses.COLS/3)
    MAX_WIN_HEIGHT = int(curses.LINES) - CONTROLS_LINES
    curses.start_color()
    curses.use_default_colors()
    curses.noecho()
    curses.cbreak()

    # init the three windows
    left = curses.newwin(curses.LINES, MAX_WIN_WIDTH, 0, 0)
    center = curses.newwin(curses.LINES, MAX_WIN_WIDTH, 0, MAX_WIN_WIDTH)
    right = curses.newwin(curses.LINES, MAX_WIN_WIDTH, 0, 2 * MAX_WIN_WIDTH)
    bottom = curses.newwin(CONTROLS_LINES, curses.COLS, MAX_WIN_HEIGHT, 0)
    stdscr.refresh()

    # draw the left column
    write_windowtitle(left, "Backlog")
    write_to_window(left, todo_tasks)
    left.refresh()

    # draw the center column
    write_windowtitle(center, "In Progress")
    write_to_window(center, started_tasks)
    center.refresh()

    # draw the right column
    write_windowtitle(right, "Done")
    write_to_window(right, completed_tasks, curses.A_ITALIC)
    right.refresh()

    write_windowtitle(bottom, "Controls")
    bottom.border(0)
    bottom.refresh()

    stdscr.getkey()

    curses.nocbreak()
    curses.endwin()


if __name__ == '__main__':
    curses.wrapper(main)