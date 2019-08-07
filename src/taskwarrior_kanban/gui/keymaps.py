    def somefunc():
        while True:
        key = stdscr.getkey()
        cur_y, cur_x = stdscr.getyx()
        if key == 'j':
            stdscr.move(cur_y +1, cur_x)
        elif key == 'k':
            stdscr.move(cur_y -1, cur_x)
        elif key == 'l':
            stdscr.move(cur_y, cur_x + MAX_WIN_WIDTH)
        elif key == 'h':
            stdscr.move(cur_y, cur_x - MAX_WIN_WIDTH)
        elif key == 'q':
            break
        else:
            break
