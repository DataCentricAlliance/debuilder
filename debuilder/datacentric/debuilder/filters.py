import os
import subprocess

def filter_all(path, files):
    """Use it to take all files"""
    return []

def filter_python(path, files):
    """Use it to filter python *.pyc and *.swp files"""
    ignore_files = []
    ignore_file_paths = []
    for file in files:
        file_path = os.path.join(path, file)
        if os.path.isfile(file_path) and \
           (file.endswith(".pyc") or file.endswith(".swp")):
            ignore_files.append(file)
            ignore_file_paths.append(file_path)

    for path in ignore_file_paths:
        print "ignore file:", path, "filter: python"
    
    return ignore_files

def filter_git(path, files):
    """Use it to take files that are already added to git"""
    def under_git(file_path):
        print "git ls-files --error-unmatch " + file_path

        child = subprocess.Popen("git ls-files --error-unmatch " + file_path,
            stdout=subprocess.PIPE, shell=True)
        streamdata = child.communicate()[0]
        return child.returncode == 0

    ignore_files = []
    ignore_file_paths = []
    for file in files:
        file_path = os.path.join(path, file)
        if os.path.isfile(file_path) and not under_git(file_path):
            ignore_files.append(file)
            ignore_file_paths.append(file_path)

    for path in ignore_file_paths:
        print "ignore file:", path, "filter: git"
    
    return ignore_files
       
