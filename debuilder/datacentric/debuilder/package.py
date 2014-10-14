import datetime
import os
import re
import shutil
import string
import subprocess
import time

from debian.changelog import Changelog
import pytz

import common

def init_build_dir():
    if os.path.exists(common.BUILD_DIR):
        shutil.rmtree(common.BUILD_DIR)
    os.makedirs(common.BUILD_DIR)

def changelog_version(file):
    if os.path.getsize(file) == 0:
        return Version("0.0.0-0")

    with open(file, 'r') as infile:
        changelog = Changelog(infile, strict = False)
        return Version(str(changelog.get_version()))

class Version:
    def __init__(self, str_version):
        self.parts = re.findall(r"[\w']+", str_version)
        assert len(self.parts) == 4, "bad version format: " + str_version
        self.parts = map(lambda x: int(x), self.parts)

        self.names = {"maj": 0, "min": 1, "mntn": 2, "build": 3}

    def __str__(self):
        return "%d.%d.%d-%d" % tuple(self.parts)

    def increment(self, tag):
        self.parts[self.names[tag]] += 1
        for part_id in range(self.names[tag] + 1, len(self.parts)):
            self.parts[part_id] = 0

class Package:
    """Full package description"""
    def __init__(self, name, description, section,
            depends="", build_depends="", conflicts="",
            provide="", architecture="all", commands=[]):
        """
        :param name: package name
        :param description: package description
        :param section: package section
        :param depends: package dependencies from another debian packages
        :param build_depends: package build dependencies from another debian packages
        :param conflicts: package conflicts
        :param provide: name of virtual package
        :param architecture: package architecture
        :param commands: description how to build package
        """
       
        self.name = name
        self.package_dir = os.path.join(common.BUILD_DIR, self.name)
        self.debian_dir = os.path.join(self.package_dir, 'debian')
        self.changelog = os.path.join('debian', 'changelog')
        self.maintainer = "%s <%s>" % (os.getenv('DEBFULLNAME'),
                                       os.getenv('DEBEMAIL'))
        self.section = section
        self.description = description
        self.build_depends = ', '.join(filter(None,
            ("debhelper (>= 9)", build_depends)))
        self.architecture = architecture
        self.depends = depends
        self.conflicts = conflicts
        self.provide = provide
        self.commands = commands
        self.extra_postinst = ""
        self.extra_postrm = ""
        self.version = changelog_version(self.changelog)

    def execute_commands(self):
        for command in self.commands:
            command.execute(self)

    def create_debian_control(self):
        template_file = os.path.join(common.TEMPLATES_DIR, 'control')
        package_file = os.path.join(self.debian_dir, 'control')
        
        control_content = None
        with open(template_file, 'r') as infile:
            control_content = string.Template(infile.read()).substitute(
                name = self.name, maintainer = self.maintainer,
                section = self.section, version = self.version,
                build_depends = self.build_depends, architecture = self.architecture,
                depends = self.depends, provide=self.provide,
                conflicts = self.conflicts, description = self.description)

        with open(package_file, 'w') as output:
            output.write(control_content)

    def create_debian_rules(self):
        shutil.copyfile(
            os.path.join(common.TEMPLATES_DIR, 'rules'),
            os.path.join(self.debian_dir, 'rules'))

    def create_debian_install(self):
        with open(os.path.join(self.debian_dir, 'install'), 'w') as outfile:
            to_install = [ "/" + f for f in os.listdir(self.package_dir)
                                       if f != "debian" ]
            for path in to_install:
                outfile.write(path + '\n')

    def create_debian_compat(self):
        with open(os.path.join(self.debian_dir, 'compat'), 'w') as output:
            output.write("9")

    def copy_debian_dir(self):
        debian_files = os.listdir('debian')
        for file_name in debian_files:
            full_file_name = os.path.join('debian', file_name)
            shutil.copy(full_file_name, os.path.join(self.debian_dir, file_name))

    def write_extra_postinst(self):
        postinst_file = os.path.join(self.debian_dir, "%s.postinst" % self.name)
        with open(postinst_file, 'a') as output:
            output.write(self.extra_postinst)

    def write_extra_postrm(self):
        postrm_file = os.path.join(self.debian_dir, "%s.postrm" % self.name)
        with open(postrm_file, 'a') as output:
            output.write(self.extra_postrm)

    def init_debian_dir(self):
        os.makedirs(self.debian_dir)
        self.create_debian_control()
        self.create_debian_rules()
        self.create_debian_install()
        self.create_debian_compat()
        self.copy_debian_dir()
        self.write_extra_postinst()
        self.write_extra_postrm()

    def init_package_dir(self):
        os.makedirs(self.package_dir)
        self.execute_commands()
        self.init_debian_dir()
    
    def build(self):
        init_build_dir()
        self.init_package_dir()
        
        #b - Binary-only build.
        #us - Do not sign the source package. 
        #uc - Do not sign the .changes file.
        subprocess.call(
            "(cd %s ; debuild -i -us -uc -b)" % self.package_dir, shell=True)

    def increment_version(self, version_inc):
        print "old version: " + str(self.version)
        self.version.increment(version_inc)
        print "new version: " + str(self.version)

    def modify_changelog(self, message):
        print "changelog message: " + message
        
        changelog = None
        with open(self.changelog, 'r') as infile:
            changelog = Changelog(infile)

        changelog.new_block(package=self.name,
            version=str(self.version),
            author=self.maintainer,
            distributions="stable",
            urgency="low",
            date=datetime.datetime.now(pytz.utc).strftime("%a, %d %b %Y %H:%M:%S %z"))

        changelog.add_change('')
        changelog.add_change('  * ' + message)
        changelog.add_change('')

        with open(self.changelog, 'w') as outfile:
            changelog.write_to_open_file(outfile)

