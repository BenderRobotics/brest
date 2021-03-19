#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    brest.log_subprocess
    ~~~~~~~~~~~~~~~~~~~~

    This module implements support for logging in subprocess.

    :copyright: 2021 Bender Robotics
"""

import logging
import sys
import subprocess
import io
import time
import os

from brest.log import CharStreamHandler

if sys.platform == 'win32':
    import msvcrt
    from ctypes import windll, byref, wintypes, WinError, POINTER
    from ctypes.wintypes import HANDLE, DWORD, BOOL

    LPDWORD = POINTER(DWORD)
    PIPE_NOWAIT = wintypes.DWORD(0x00000001)
    ERROR_NO_DATA = 232
else:
    from fcntl import fcntl, F_GETFL, F_SETFL
    from os import O_NONBLOCK, read


DEVNUL = subprocess.DEVNULL
PIPE = subprocess.PIPE
STDOUT = subprocess.STDOUT


def run(args, log=False, timeout=None, buffsize=-1, executable=None, stdin=None, stdout=None,
        stderr=None, preexec_fn=None, close_fds=(sys.platform != 'win32'), shell=False, cwd=None,
        env=None, universal_newlines=None, startupinfo=None, creationflags=0, restore_signals=True,
        start_new_session=False, pass_fds=(), encoding=None, errors=None):
    """
    copy of subprocess.run function with added logging support
    """
    logger = logging.getLogger('brest').getChild('subprocess')

    if log in ['after', 'continuous']:
        logger.info("Running subprocess: %s", " ".join(args), extra=__get_cmd(args))

        if log == 'continuous':
            process = _run_continuous_logging(args, timeout, buffsize, executable, stdin, stdout,
                                              stderr, preexec_fn, close_fds, shell, cwd, env,
                                              universal_newlines, startupinfo, creationflags,
                                              restore_signals, start_new_session, pass_fds,
                                              encoding=encoding, errors=errors)
        else:
            process = _run_logging(args, timeout, buffsize, executable, stdin, stdout, stderr,
                                   preexec_fn, close_fds, shell, cwd, env, universal_newlines,
                                   startupinfo, creationflags, restore_signals, start_new_session,
                                   pass_fds, encoding=encoding, errors=errors)

        return process

    process = subprocess.Popen(args, buffsize, executable, stdin, stdout, stderr, preexec_fn,
                               close_fds, shell, cwd, env, universal_newlines, startupinfo, creationflags,
                               restore_signals, start_new_session, pass_fds, encoding=encoding,
                               errors=errors)
    if timeout:
        try:
            process.wait(timeout)
        except subprocess.TimeoutExpired:
            raise TimeoutError
    else:
        process.wait()

    return process


def _run_continuous_logging(args, timeout=None, buffsize=-1, executable=None, stdin=None,
                            stdout=None, stderr=None, preexec_fn=None, close_fds=(sys.platform != 'win32'),
                            shell=False, cwd=None, env=None, universal_newlines=None,
                            startupinfo=None, creationflags=0, restore_signals=True,
                            start_new_session=False, pass_fds=(), encoding=None,
                            errors=None):
    """
    Real time logging for subprocess
    !This method is designed only for logger with one handler!
    """

    logger = logging.getLogger('brest').getChild('subprocess_continuous')

    # start process in another thread
    process = subprocess.Popen(args, buffsize, executable, stdin, stdout, stderr, preexec_fn,
                               close_fds, shell, cwd, env, False, startupinfo, creationflags,
                               restore_signals, start_new_session, pass_fds, encoding=encoding,
                               errors=errors)

    # set read as non blocking
    if stdout == PIPE:
        __set_pipe_nonblocking(process.stdout)
    elif stderr == PIPE:
        __set_pipe_nonblocking(process.stderr)

    back_up = bytearray()
    before = time.time()
    while process.poll() is None:
        while True:
            if timeout and time.time() - before > timeout:
                process.terminate()
                raise TimeoutError
            # peek will not work
            if stdout == PIPE:
                try:
                    output = process.stdout.read(1)
                except OSError:  # OSError for windows if pipe is empty
                    output = None

            elif stderr == PIPE:
                try:
                    output = process.stderr.read(1)
                except OSError:
                    output = None

            if output:
                # before = time.time() # uncomment to refresh timout on read
                back_up += output
                if sys.platform == "win32":
                    logger.info(output.decode('cp1250'), extra=__get_cmd(args))
                else:
                    logger.info(output.decode(), extra=__get_cmd())
            else:
                break

    # replace original stream by our backup
    fake_buffered_reader = io.BufferedReader(io.BytesIO(back_up))
    if stdout == PIPE:
        process.stdout = fake_buffered_reader
    elif stderr == PIPE:
        process.stderr = fake_buffered_reader

    return process


def _run_logging(args, timeout=None, buffsize=-1, executable=None, stdin=None, stdout=None,
                 stderr=None, preexec_fn=None, close_fds=(sys.platform != 'win32'), shell=False,
                 cwd=None, env=None, universal_newlines=None, startupinfo=None, creationflags=0,
                 restore_signals=True, start_new_session=False, pass_fds=(),
                 encoding=None, errors=None):
    """
    Creates subprocess and logs it outputs
    ! output stream is replaced with copy !
    """

    logger = logging.getLogger('brest').getChild('subprocess')

    # start subprocess
    process = subprocess.Popen(args, buffsize, executable, stdin, stdout, stderr, preexec_fn,
                               close_fds, shell, cwd, env, universal_newlines, startupinfo, creationflags,
                               restore_signals, start_new_session, pass_fds, encoding=encoding,
                               errors=errors)
    # wait for it to finish
    process.wait(timeout)

    if stdout == PIPE:
        output = process.stdout.read()
    elif stderr == PIPE:
        output = process.stderr.read()

    # log program output
    for line in output.splitlines():
        if sys.platform == "win32":
            logger.info(line.decode('cp1250'), extra=__get_cmd(args))
        else:
            logger.info(line.decode(), extra=__get_cmd(args))

    # replace original stream with fake one
    backup = bytearray()
    backup += output
    fake_buffered_reader = io.BufferedReader(io.BytesIO(backup))

    if stdout == PIPE:
        process.stdout = fake_buffered_reader
    elif stderr == PIPE:
        process.stderr = fake_buffered_reader

    return process


def __set_pipe_nonblocking(pipefd):
    if sys.platform == 'win32':
        SetNamedPipeHandleState = windll.kernel32.SetNamedPipeHandleState
        SetNamedPipeHandleState.argtypes = [HANDLE, LPDWORD, LPDWORD, LPDWORD]
        SetNamedPipeHandleState.restype = BOOL

        h = msvcrt.get_osfhandle(pipefd.name)

        res = windll.kernel32.SetNamedPipeHandleState(h, byref(PIPE_NOWAIT), None, None)
        if res == 0:
            print(WinError())
            return False
        return True
    else:
        flags = fcntl(pipefd, F_GETFL)
        fcntl(pipefd, F_SETFL, flags | O_NONBLOCK)


def __get_cmd(args):
    cmd = os.path.basename(args[0])
    if len(cmd) > 25:
        cmd = cmd[:25] + "..."
    return {'cmd': cmd}
