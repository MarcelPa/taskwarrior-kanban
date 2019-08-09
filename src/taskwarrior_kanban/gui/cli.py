import argparse
import curses

import taskwarrior_kanban.main 
import taskwarrior_kanban.gui.keymap
from taskwarrior_kanban.gui.curses_windows import MainWindow

description="""
Some really nice text.
"""

def create_parser():
    """
    Creates a ArgumentParser for the cli of taskwarrior-kanban.

    >>> parser = create_parser()
    >>> args = parser.parse_args([''])
    >>> args.taskwarrior_args
    ['']
    >>> args = parser.parse_args(['project:home'])
    >>> args.taskwarrior_args
    ['project:home']
    >>> args = parser.parse_args(['project:home','due:1w'])
    >>> args.taskwarrior_args
    ['project:home', 'due:1w']
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("taskwarrior_args", 
            help="(optional) Arguments that will be passed to taskwarrior, e.g. in order to set a filter for a project.",
            nargs='*')

    return parser

def redraw(main_window, tasks, selection):
    for i, win in enumerate(main_window.get_window()):
        if i < len(tasks):
            win.draw(tasks[i])
        else:
            win.draw()
    # TODO: finish view before controls
    #main_window.get_window(selection[0]).draw(tasks[selection[0]], selection[1])
    main_window.control.draw(element=tasks[selection[0]][selection[1]])
    main_window.refresh()

def main():
    # get the arguments from the commandline
    args = create_parser().parse_args()

    # gather all tasks
    tasks = list(taskwarrior_kanban.main.gather_tasks(args.taskwarrior_args))

    # create the main windows
    main = MainWindow()
    # create the four sub-windows
    main.create_windows()
    # set a selection variable, a tuple of (selected window, selected item)
    selection = (0,1)

    # draw the three task windows
    redraw(main, tasks, selection)

    loop = True
    while loop:
        input_key = main.scr.getkey()
        # TODO: work on displaying everything first. Controls will follow afterwards
        #action = taskwarrior_kanban.gui.keymap.fire(input_key)
        action = None
        if action is not None:
            main, task, selection = action(main, tasks, selection)
            
            loop = True
        else:
            loop = False

    main.destroy()
