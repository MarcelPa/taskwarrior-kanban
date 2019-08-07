import curses

# Config: Layout variables
CONTROLS_LINES = 7 # number of lines that will be used by the 'controls' field
BORDER_CELLS = 1 # number of cells that will be used to pad the colums on the left and right

def debug_init():
    """
    Calls the curses wrapper for development use.
    """
    return curses.wrapper(initialize)

def initialize(stdscr=None):
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

    # init the three windows
    left = curses.newwin(MAX_WIN_HEIGHT, MAX_WIN_WIDTH, 0, 0)
    center = curses.newwin(MAX_WIN_HEIGHT, MAX_WIN_WIDTH, 0, MAX_WIN_WIDTH)
    right = curses.newwin(MAX_WIN_HEIGHT, MAX_WIN_WIDTH, 0, 2 * MAX_WIN_WIDTH)
    bottom = curses.newwin(CONTROLS_LINES, curses.COLS, MAX_WIN_HEIGHT, 0)
    stdscr.refresh()

    return (left, center, right, bottom)

def deinitialize():
    """
    De-Initializes curses according to the curses docs
    """
    curses.nocbreak()
    curses.endwin()


def write_to_window(win, list, attr=curses.A_NORMAL):
    """
    Writes a list of ToDos to a curses window.

    win is the curses window that will be written to, list equals to a list of
    tasks that will be written to win and attr are optional curses attributes
    that can be added to writing. The list will be truncated if it is longer
    than the window height.
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
        

        # Write description to the window
        win.addstr(i+3, 2,f"{desc}", colorize[i%2] | attr)

    win.refresh()

def write_windowtitle(win, title):
    """ 
    Writes a title to window such that it is centered in the first line of a window.
    """

    win_width = win.getmaxyx()[1]
    if len(title) > win_width:
        title = f"{title[:win_width-3]}..."
    win.addstr(1, int(win_width/2 - len(title)/2), title, curses.A_BOLD)
