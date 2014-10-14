#!/usr/bin/python
 
from datacentric.debuilder import *
 
dispatch(
    Package(
        name = "datacentric-env-testing",
        section = "devel",
        provide = "datacentric-env",
        description = "Testing environment",
        conflicts = "datacentric-env-development, datacentric-env-production", 

        commands = [Copy(["env.cfg"], "/etc/datacentric/env/")]
    )
)
