#!/usr/bin/python
 
from datacentric.debuilder import *
 
dispatch(
    Package(
        name = "datacentric-env-production",
        section = "devel",
        provide = "datacentric-env",
        description = "Production environment",
        conflicts = "datacentric-env-testing, datacentric-env-development", 

        commands = [Copy(["env.cfg"], "/etc/datacentric/env/")]
    )
)
