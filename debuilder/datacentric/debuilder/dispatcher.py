import functools
import os
import subprocess

import opster

import common

def scp(source, target):
    subprocess.call("scp %s %s" % (source, target), shell=True)

def increment_version(version, message, package):
    assert message != "" "empty message is prohibited"
    assert version != "" "empty version incremental tag is prohibited"
    package.increment_version(version)
    package.modify_changelog(message)

@opster.command(usage='[-v (maj|min|mntn|build) -m CHANGELOG_MESSAGE]')
def build(package,
          version=('v', '', 'how to increment version (maj|min|mntn|build)'),
          message=('m', '', 'chagelog message')):
    """
    use ./deb.py build to rebuild package
    use ./deb.py build -v min -m "message" to modify version, changelog and rebuld package
    """
    if version and message:
        increment_version(version, message, package)
    package.build()

@opster.command()
def pub(package):
    """
    submit package to debian repository, uses DEBREPOSITORY environment variable
    """
    scp(os.path.join(common.BUILD_DIR, package.name) + "*.deb", common.REPOSITORY)
    scp(os.path.join(common.BUILD_DIR, package.name) + "*.changes", common.REPOSITORY)

def middleware(package, func):
    def inner(*args, **kwargs):
        if func.__name__ == 'help_inner':
             return func(*args, **kwargs)
        return func(package, *args, **kwargs)
    return inner

def dispatch(package):
    """Process command line
    :param package: working package
    """
    opster.dispatch(middleware=functools.partial(middleware, package))

