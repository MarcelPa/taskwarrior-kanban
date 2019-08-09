import curses

import taskwarrior_kanban.main

class MainWindow:
    """
    Definition of the layout of curses windows, aka the standard screen 
    created by curses.initscr().
    """

    def __init__(self):
        self.scr = curses.initscr()
        self.control_lines = 9
        self.MAX_WIN_WIDTH = int(curses.COLS/3)
        self.MAX_WIN_HEIGHT = int(curses.LINES) - self.control_lines
        curses.start_color()
        curses.use_default_colors()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.scr.clear()

    def create_windows(self):
        """
        Creates the main layout for all necessary windows.

        +-----------+-------------+----------+
        |  Backlog  | In Progress |   Done   |
        |           |             |          |
        |           |             |          |
        +-----------+-------------+----------+
        |            Control Pane            |
        +------------------------------------+
        """
        self.left = TaskWindow(self.MAX_WIN_HEIGHT, self.MAX_WIN_WIDTH, 0, 0, "Backlog")
        self.center = TodoWindow(self.MAX_WIN_HEIGHT, self.MAX_WIN_WIDTH, 0, self.MAX_WIN_WIDTH, "In Progress")
        self.right = TaskWindow(self.MAX_WIN_HEIGHT, self.MAX_WIN_WIDTH, 0, 2 * self.MAX_WIN_WIDTH, "Done")
        self.control = ControlWindow(self.control_lines, curses.COLS, self.MAX_WIN_HEIGHT, 0)
        self.scr.refresh()

    def get_window(self, i=None):
        """
        Return a sub-window by number if a valid number is supplied, reutnrs
        a list of all windows otherwise.

        i == 1: left
        i == 2: center
        i == 3: right
        i == 4: control
        """
        windows = [self.left, self.center, self.right, self.control]
        if i is None or i < 0 or i >= len(windows):
            return windows
        else:
            return windows[i]


    def destroy(self):
        self.scr.clear()
        self.scr.refresh()
        curses.nocbreak()
        curses.endwin()

    def refresh(self):
        self.scr.refresh()
        
class CursesWindow:
    """
    Wrapper-class for a curses window with a title.
    """

    def __init__(self, height, width, y, x, title, content=[], border_cells=1):
        """
        Initialize new curses.window with size height x width at position (y,x)
        and with the title of title and the content of content.
        """
        self.window = curses.newwin(height, width, y, x)
        self.title = title
        self.content = content
        self.border_cells = border_cells

        # also set the colors
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        self.colorize = (curses.A_NORMAL, curses.color_pair(1))

    def refresh(self):
        """
        API implementation for curses.window: calls refresh on the created window
        instance.
        """
        self.window.refresh()

    # func=None allows this function to be used as a decorator (I guess)
    def draw(self, func=None):
        """
        This function will draw the title to the window it represents.
        """
        # get the window measurements
        win_height, win_width = self.window.getmaxyx()

        # draw the title
        title_todraw = self.title
        if len(self.title) > win_width:
            title_todraw = f"{title[:win_width-3]}..."
        self.window.addstr(1, int(win_width/2 - len(title_todraw)/2), title_todraw, curses.A_BOLD)
        self.refresh()

class TodoWindow(CursesWindow):
    """
    Extend a CursesWindow to show a list of todos as a content.
    """

    def draw(self, list, selected=-1, attr=curses.A_NORMAL):
        # draw generics
        super().draw()

        # get the window measurements
        win_height, win_width = self.window.getmaxyx()

        # if the list is longer than the maximum height, truncate it TODO: make something smarter here (scrolling?)
        if len(list) > win_height:
            list = list[:win_height-1]

        # iterate through all ToDos within the list
        for i, item in enumerate(list):
            # This one defines the layout
            desc = f"{item['description']} [{item['project']}]"
            # Truncate the description if too long
            if len(desc) > win_width - self.border_cells*2:
                # maximum length: window    - border         - length of project title - (space and square bracket chars ( = 3)) - (three dots)
                max_desc_length = win_width - self.border_cells*2 - len(item['project']) - 3 - 3
                desc = f"{item['description'][:max_desc_length]}... [{item['project']}]"
            # If not long enough, pad with spaces in order to paint a whole line
            else:
                desc = "{:<{}}".format(desc, win_width-2)
            
            if selected == i:
                highlight = curses.A_REVERSE
            else:
                highlight = curses.A_NORMAL

            # newlines are not supposed to be drawn
            desc = desc.replace('\n', ' ')

            # Write description to the window
            self.window.addstr(i+3, 2,f"{desc}", self.colorize[i%2] | attr | highlight)

        self.refresh()

class TaskWindow(CursesWindow):
    """
    Extend a CursesWindow to show a list of todos as a content.
    """

    def draw(self, list, selected=-1, attr=curses.A_NORMAL):
        # draw generics
        super().draw()

        # get the window measurements
        win_height, win_width = self.window.getmaxyx()

        # if the list is longer than the maximum height, truncate it TODO: make something smarter here (scrolling?)
        if len(list) > win_height:
            list = list[:win_height-1]

        # iterate through all ToDos within the list
        for i, item in enumerate(list):
            # This one defines the layout
            desc = f"{item['description']} [{item['project']}]"
            # Truncate the description if too long
            if len(desc) > win_width - self.border_cells*2:
                # maximum length: window    - border         - length of project title - (space and square bracket chars ( = 3)) - (three dots)
                max_desc_length = win_width - self.border_cells*2 - len(item['project']) - 3 - 3
                desc = f"{item['description'][:max_desc_length]}... [{item['project']}]"
            # If not long enough, pad with spaces in order to paint a whole line
            else:
                desc = "{:<{}}".format(desc, win_width-2)
            
            if selected == i:
                highlight = curses.A_REVERSE
            else:
                highlight = curses.A_NORMAL

            # newlines are not supposed to be drawn
            desc = desc.replace('\n', ' ')

            # Write description to the window
            self.window.addstr(i+3, 2,f"{desc}", self.colorize[i%2] | attr | highlight)

        self.refresh()

class ControlWindow(CursesWindow):
    """
    Extend a CursesWindow to show controls and details to a selected task.
    """
    
    def __init__(self, height, width, y, x):
        super().__init__(height, width, y, x, "Controls")
        # TODO: finish view before controls
        #self.window.addstr(height-2, 2, f"Controls show up here")

    def draw(self, element=None):
        """
        Method that draws the control panel, including details to a task if
        supplied in element.
        """
        # draw a border
        self.window.border(0)

        # draw details to an element, if supplied
        if element is not None:
            self.window.addstr(1, 1, f"Task: {element['description']}{' ' * (curses.COLS - len(element['description']) - 8)}")
            self.window.addstr(2, 1, f"{taskwarrior_kanban.main.format_task_details(element)}")

        self.refresh()
