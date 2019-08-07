from setuptools import find_packages, setup

with open('README.md', 'r') as readme:
    long_description = readme.read()

setup(
        name='taskwarrior_kanban',
        version='0.1.0',
        author='Marcel Parciak',
        author_email='marcel.parciak@gmail.com',
        description='A curses kanban board for TaskWarrior',
        long_description=long_description,
        long_description_content_type='text/markdown',
        url='https://github.com/MarcelPa/taskwarrior-kanban',
        packages=find_packages('src'),
        package_dir={'': 'src'},
        entry_points={
            'console_scripts': [ 'taskwarrior_kanban=taskwarrior_kanban.gui.cli:main' ],
            }
)
