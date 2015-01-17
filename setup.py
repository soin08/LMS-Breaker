"""
File based on a contribution from Josh Immanuel. Use via

python setup-py2exe.py py2exe

which will create a dist folder containing the .exe, the python DLL, and a
few other DLL deemed by py2exe to be critical to the application execution.

The contents of the dist folder should then be packaged using a tool such
as NSIS or Inno Setup. The py2exe page has an example for NSIS.
"""

from distutils.core import setup

import py2exe

setup (
    name='LMS Breaker',
    description="Решает любое задание на платформе Cambridge LMS за несколько секунд.",
    version="1.0",

    console=[{'script': 'breaker_cmd.py'}],
    options={ 'py2exe': {
                'packages': 'lmsbreaker',
                'includes': None}
            },
    )
