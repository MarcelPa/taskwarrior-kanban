import taskwarrior_kanban.gui.cli

def selection(func, main_window, tasks, selection):
    func(main_window, tasks, selection)
    taskwarrior_kanban.gui.cli.redraw(main_window, tasks, selection)

def fire(key):
    """
    Specifies what should happend when a certain key is pressed.
    """

    if key == 'k':
        def select_up(main_window, tasks, selection):
            win, item = selection
            if item > 0:
                item -= 1
            else:
                item = 0
            selection = (win, item)
            taskwarrior_kanban.gui.cli.redraw(main_window, tasks, selection)
            return (main_window, tasks, selection)

        return select_up

    elif key == 'j':
        def select_down(main_window, tasks, selection):
            win, item = selection
            item += 1
            if item >= len(tasks[win]):
                item = len(tasks[win])-1
            selection = (win, item)
            main_window.control.window.addstr(5, 40, f"{selection}")
            taskwarrior_kanban.gui.cli.redraw(main_window, tasks, selection)
            return (main_window, tasks, selection)

        return select_down

    elif key == 'l':
        def select_right(main_window, tasks, selection):
            win, item = selection
            win += 1
            if win >= len(main_window.get_window()):
                win = len(main_window.get_window()) -1
            if item < len(tasks[win]):
                selection = (win, item)
            else:
                selection = (win, len(tasks[win])-1)
            taskwarrior_kanban.gui.cli.redraw(main_window, tasks, selection)
            return (main_window, tasks, selection)

        return select_right

    elif key == 'h':
        def select_left(main_window, tasks, selection):
            win, item = selection
            if win > 0:
                win -=1
            else:
                win = 0
            selection = (win, item)
            taskwarrior_kanban.gui.cli.redraw(main_window, tasks, selection)
            return (main_window, tasks, selection)

        return select_left

    elif key == 'q':
        return None
    else:
        return None
    return None
