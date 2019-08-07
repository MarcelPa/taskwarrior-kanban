import argparse

import taskwarrior_kanban.gui.curses as twk_curses
import taskwarrior_kanban.gui.cli
import taskwarrior_kanban.main 

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

def main():
    # get the arguments from the commandline
    args = create_parser().parse_args()

    # start curses, which returns four windows
    left, center, right, control = taskwarrior_kanban.gui.curses.debug_init()
    todo_tasks, started_tasks, completed_tasks = taskwarrior_kanban.main.gather_tasks()

    # populate the left column
    twk_curses.write_windowtitle(left, "Backlog")
    twk_curses.write_to_window(left, todo_tasks)

    # populate the center column
    twk_curses.write_windowtitle(center, "In Progress")
    twk_curses.write_to_window(center, started_tasks)

    # populate the right column
    twk_curses.write_windowtitle(right, "Done")
    twk_curses.write_to_window(right, completed_tasks)

    # draw the controls panel
    twk_curses.write_windowtitle(control, "Controls")
    control.border(0)
    control.refresh()

    while twk_curses.wait_for_input():
        pass

    twk_curses.deinitialize()

if __name__ == "__main__":
    main()
