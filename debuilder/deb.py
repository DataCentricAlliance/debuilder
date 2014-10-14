#!/usr/bin/python

from datacentric.debuilder import *

dispatch(
    Package(
        name = "datacentric-debuilder",
        section = "devel",
        description = "Tool to simplify debian packages creation",
        depends = "debhelper, devscripts, python-opster, python-debian, python-tz",
        
        commands = [Copy(["datacentric"], PYTHONPATH)]
    )
)

