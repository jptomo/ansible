# (c) 2012-2014, Michael DeHaan <michael.dehaan@gmail.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

import os
import tempfile


_IS_WIN = (os.name == 'nt')


if _IS_WIN:
    getpwnam = None
    LOCK_EX = None
    LOCK_UN = None
    lockf = None
    flockf = None
    tcgetattr = None
    tcsetattr = None
    tcflush = None
    TCSADRAIN = None
    TCIFLUSH = None
    setraw = None
    openlog = None
    syslog = None
    getgrgid = None
    getgrnam = None

else:
    import pwd
    import fcntl
    import termios
    import tty
    import syslog
    import grp

    getpwnam = pwd.getpwnam
    LOCK_EX = fcntl.LOCK_EX
    LOCK_UN = fcntl.LOCK_UN
    lockf = fcntl.lockf
    flockf = fcntl.flock
    tcgetattr = termios.tcgetattr
    tcsetattr = termios.tcsetattr
    tcflush = termios.tcflush
    TCSADRAIN = termios.TCSADRAIN
    TCIFLUSH = termios.TCIFLUSH
    setraw = tty.setraw
    openlog = syslog.openlog
    syslog = syslog.syslog
    getgrgid = grp.getgrgid
    getgrnam = grp.getgrnam


def get_local_username():
    if _IS_WIN:
        return os.environ['USERNAME']

    else:
        return pwd.getpwuid(os.geteuid())[0]


def get_file_owner_name(filepath):
    if _IS_WIN:
        pass

    else:
        return pwd.getpwuid(os.stat(filepath).st_uid).pw_name


def log_lockfile():
    if _IS_WIN:
        pass

    else:
        # create the path for the lockfile and open it
        tempdir = tempfile.gettempdir()
        uid = os.getuid()
        path = os.path.join(tempdir, ".ansible-lock.%s" % uid)
        lockfile = open(path, 'w')
        # use fcntl to set FD_CLOEXEC on the file descriptor,
        # so that we don't leak the file descriptor later
        lockfile_fd = lockfile.fileno()
        old_flags = fcntl.fcntl(lockfile_fd, fcntl.F_GETFD)
        fcntl.fcntl(lockfile_fd, fcntl.F_SETFD, old_flags | fcntl.FD_CLOEXEC)
        return lockfile


LOG_LOCK = log_lockfile()


def log_flock(runner):
    if _IS_WIN:
        pass

    else:
        if runner is not None:
            try:
                fcntl.lockf(runner.output_lockfile, fcntl.LOCK_EX)
            except OSError:
                # already got closed?
                pass
        else:
            try:
                fcntl.lockf(LOG_LOCK, fcntl.LOCK_EX)
            except OSError:
                pass


def log_unflock(runner):
    if _IS_WIN:
        pass

    else:
        if runner is not None:
            try:
                fcntl.lockf(runner.output_lockfile, fcntl.LOCK_UN)
            except OSError:
                # already got closed?
                pass
        else:
            try:
                fcntl.lockf(LOG_LOCK, fcntl.LOCK_UN)
            except OSError:
                pass
