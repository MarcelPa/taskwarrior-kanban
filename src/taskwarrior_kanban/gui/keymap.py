import curses

def get_mapped_action(key, active_window):
    """
    Specifies what should happen when a certain key is pressed. 
    """

    if key == ord('k') or key == curses.KEY_UP:
        return active_window.select_up

    elif key == ord('j') or key == curses.KEY_DOWN:
        return active_window.select_down

    elif key == ord('l') or key == curses.KEY_RIGHT:
        return active_window.select_right

    elif key == ord('h') or key == curses.KEY_LEFT:
        return active_window.select_left

    elif key == ord('q'):
        return None

    else:
        print(key)
        return None
