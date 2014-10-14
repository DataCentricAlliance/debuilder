import glob
import os
import re
import shutil

from filters import filter_git

class Command:
    def execute(self, package):
        pass

class Mkdir(Command):
    """Create directory"""

    def __init__(self, dir, user="root", group="root"):
        """
        :param dir: absolute directory path
        :param user: directory owner
        :param group: directory group
        """
        self.dir = dir
        self.user = user
        self.group = group

    def execute(self, package):
        os.makedirs(os.path.join(package.package_dir, self.dir[1:]))
        package.extra_postinst += "\nchown -R %s:%s %s\n" % (self.user, self.group, self.dir)
 

class Copy(Command):
    """Add file to package"""

    def __init__(self, sources, destination, filter=filter_git):
        """
        :param sources: list of relative paths (or wildcards) of source files
        :param destination: absolute destination path
        :param filter: filter for source files
        """
        self.sources = sources
        #remove first '/' for function os.path.join
        self.dest = destination[1:]
        self.filter = filter

    def execute(self, package):
        rename = self.dest[-1] != "/"

        dest_dirname = os.path.dirname(self.dest) if rename else self.dest
        target_dir = os.path.join(package.package_dir, dest_dirname)
        if not os.path.isdir(target_dir):
            os.makedirs(target_dir)
        
        for wildcard in self.sources:
            for source_path in glob.iglob(wildcard):
                target_path = os.path.join(target_dir,
                    os.path.basename(self.dest if rename else source_path))
                
                if os.path.isfile(source_path):
                    shutil.copy(source_path, target_path)
                else:
                    shutil.copytree(source_path, target_path, ignore=self.filter)

class EnvLink(Command):
    """Create environment link in postinst script"""

    def __init__(self, env_pattern, link_name = None):
        """
        :param env_pattern: files pattern (for example: datacentric-$ENV.cfg)
        :param link_name: link name that will be created (by default it's env_pattern without ".$ENV")
        """
        self.env_pattern = env_pattern
        self.link_name = link_name if link_name else \
            re.sub(r'.\$ENV', r'', env_pattern)

    def execute(self, package):
        package.extra_postinst += "\nENV=$(cat /etc/facetz/env/env.cfg)\nln -sf %s %s\n" % (
                self.env_pattern, self.link_name)
        
        package.extra_postrm += "\nrm -rf %s\n" % self.link_name

        if "facetz-env" not in package.depends:
            package.depends += ", facetz-env"

