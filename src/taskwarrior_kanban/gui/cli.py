import argparse
import curses

import taskwarrior_kanban.main 
import taskwarrior_kanban.gui.keymap

# Config: Layout variables
CONTROLS_LINES = 7 # number of lines that will be used by the 'controls' field
BORDER_CELLS = 1 # number of cells that will be used to pad the colums on the left and right

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

def initialize_curses(stdscr=None):
    """
    Initializes the basic layout for taskwarrior_kanbar using curses.

    The basic layout uses three equal width columns for 'Backlog', 
    'In Progress' and 'Done' and a bottom window that displays some controls
    as well as detailed information.
    """

    # enable curses.wrapper to work properly
    if stdscr is None:
        stdscr = curses.initscr()

    MAX_WIN_WIDTH = int(curses.COLS/3)
    MAX_WIN_HEIGHT = int(curses.LINES) - CONTROLS_LINES
    curses.start_color()
    curses.use_default_colors()
    curses.noecho()
    curses.cbreak()
    stdscr.clear()

    # init the three windows
    left = curses.newwin(MAX_WIN_HEIGHT, MAX_WIN_WIDTH, 0, 0)
    center = curses.newwin(MAX_WIN_HEIGHT, MAX_WIN_WIDTH, 0, MAX_WIN_WIDTH)
    right = curses.newwin(MAX_WIN_HEIGHT, MAX_WIN_WIDTH, 0, 2 * MAX_WIN_WIDTH)
    bottom = curses.newwin(CONTROLS_LINES, curses.COLS, MAX_WIN_HEIGHT, 0)
    stdscr.refresh()

    return (left, center, right, bottom, stdscr)


def deinitialize_curses():
    """
    De-Initializes curses according to the curses docs
    """
    curses.nocbreak()
    curses.endwin()



def write_to_window(win, list, attr=curses.A_NORMAL, selected=None):
    """
    Writes a list of ToDos to a curses window.

    win is the curses window that will be written to, list equals to a list of
    tasks that will be written to win and attr are optional curses attributes
    that can be added to writing. The list will be truncated if it is longer
    than the window height. selected indicates that in this supplied list, the
    nth item is currently selected, hence it should be highlighted.
    """

    # get the window measurements
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
        
        if selected is not None and selected == i:
            highlight = curses.A_REVERSE
        else:
            highlight = curses.A_NORMAL

        # Write description to the window
        win.addstr(i+3, 2,f"{desc}", colorize[i%2] | attr | highlight)

    win.refresh()

def write_windowtitle(win, title):
    """ 
    Writes a title to window such that it is centered in the first line of a window.
    """

    win_width = win.getmaxyx()[1]
    if len(title) > win_width:
        title = f"{title[:win_width-3]}..."
    win.addstr(1, int(win_width/2 - len(title)/2), title, curses.A_BOLD)

def draw_task_windows(windows, titles, lists, selections):

    if len(windows) != len(titles) or len(windows) != len(lists) or len(windows) != len(selections):
        # problem!
        return None

    for i in range(0, len(windows)):
        write_windowtitle(windows[i], titles[i])
        write_to_window(windows[i], lists[i], selected=selections[i])


def main():
    # get the arguments from the commandline
    args = create_parser().parse_args()

    # start curses, which returns four windows
    left, center, right, control, scr = initialize_curses()
    todo_tasks, started_tasks, completed_tasks = taskwarrior_kanban.main.gather_tasks(args.taskwarrior_args)

    draw_task_windows([left, center, right], ["Backlog", "In Progress", "Done"], [todo_tasks, started_tasks, completed_tasks], [0, None, None])

    # draw the controls panel
    write_windowtitle(control, "Controls")
    control.border(0)
    control.refresh()

    loop = True
    while loop:
        input_key = scr.getkey()
        loop = taskwarrior_kanban.gui.keymap.get_input(input_key)

    deinitialize_curses()
