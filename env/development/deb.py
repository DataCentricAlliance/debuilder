#!/usr/bin/python
 
from datacentric.debuilder import *
 
dispatch(
    Package(
        name = "datacentric-env-development",
        section = "devel",
        provide = "datacentric-env",
        description = "Development environment",
        conflicts = "datacentric-env-testing, datacentric-env-production", 

        commands = [Copy(["env.cfg"], "/etc/datacentric/env/")]
    )
)
