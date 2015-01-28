import requests.certs
from distutils.core import setup
import py2exe

setup (
    name='LMS Breaker',
    description="Решает любое задание на платформе Cambridge LMS за несколько секунд.",
    version="1.1",
    data_files = [ ( '', [ requests.certs.where() ] ) ],
    #console=[{'script': 'main.py'}],
    options={ 'py2exe': {
                        #'packages': 'mechanicalsoup',
                        'includes': ['sip'],
                        'optimize' : 1,
                        #'bundle_files': 1,
                        'compressed': True,
                        },
                    },
    windows = [{
                        'script' : 'lms_breaker_gui.py',
                        'dest_base' : 'breaker',
                        "icon_resources": [(1, "icon.ico")],
                        }],
    zipfile = None,
    )
