# taskwarrior-kanban: Personal Kanban Board for Taskwarrior.

`tw-kanban.py` is a Python(3) script which provides a simple [personal
Kanban](http://lifehacker.com/productivity-101-how-to-use-personal-kanban-to-visuali-1687948640)
board for the task management tool [Taskwarrior](taskwarrior.org). It sorts your tasks into the
following three categories - **Backlog**, **In Progress**, and **Done**, and generates a Kanban
board using curses in a terminal.

This project is based on (and forked from) [taskwarrior-kanban by Jithin Jith](https://github.com/j-jith/taskwarrior-kanban). Thanks to Jithin!

**Not started** category contains tasks which are pending and have not been started yet. **In
progress** category contains tasks which are pending but have been started. And **Done** category
contains the last 10 tasks which have been completed.

*This does not give you an interactive Kanban board. All changes have to be made through taskwarrior
and then `tw-kanban.py` has to be run again to regenerate the board.*

## Prerequisites

- [Taskwarrior](http://taskwarrior.org/download/) (Tested on version 2.5.1)

- Python 3.0+ (Tested on Python 3.7.4)

## Usage

- `python3 tw-kanban.py`
- ???
- Profit