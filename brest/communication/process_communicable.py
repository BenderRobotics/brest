import logging
import sys
import subprocess
import io
import time

from fcntl import fcntl, F_GETFL, F_SETFL
from os import O_NONBLOCK, read

from brest.communication import Communicable
from brest.log import CharStreamHandler, DEFAULT_LOGGING


class ProcessCommunicable(Communicable):

    DEVNUL = subprocess.DEVNULL
    PIPE = subprocess.PIPE
    STDOUT = subprocess.STDOUT

    @staticmethod
    def run(args, continuous=False, log=False, timeout=None, buffsize=-1, executable=None, stdin=None, stdout=None,
            stderr=None, preexec_fn=None, close_fds=True, shell=False, cwd=None, env=None,
            universal_newlines=None, startupinfo=None, creationflags=0, restore_signals=True,
            start_new_session=False, pass_fds=(), encoding=None, errors=None):
        """
        copy of subprocess.run function with added logging support
        """
        process = subprocess.Popen(args, buffsize, executable, stdin, stdout, stderr, preexec_fn,
                                    close_fds, shell, cwd, env, universal_newlines, startupinfo, creationflags,
                                    restore_signals, start_new_session, pass_fds, encoding=encoding,
                                    errors=errors)
        process.wait(timeout)

        return process

    @staticmethod
    def run_continuous_logging(args, timeout=None, buffsize=-1, executable=None, stdin=None,
                               stdout=None, stderr=None, preexec_fn=None, close_fds=True,
                               shell=False, cwd=None, env=None, universal_newlines=None,
                               startupinfo=None, creationflags=0, restore_signals=True,
                               start_new_session=False, pass_fds=(), encoding=None,
                               errors=None):
        """
        Real time logging for subprocess
        !This method is designed only for logger with one handler!
        """

        logger = logging.getLogger('brest')
        char_handler = CharStreamHandler(stream=sys.stdout)
        char_handler.setLevel(logging.INFO)

        logger_bckup = logger.handlers[0]

        # if formatter contains function name, replace it wil called command
        if '%(funcName)s()' in logger.handlers[0].formatter._fmt:
            cmd = " ".join(args)
            if len(cmd) > 20:
                cmd = cmd[:20] + "..."

            new_formatter = logger.handlers[0].formatter
            new_formatter._style._fmt = logger.handlers[0].formatter._style._fmt.replace("%(funcName)s()", cmd)
            char_handler.setFormatter(new_formatter)
        else:
            char_handler.setFormatter(logger.handlers[0].formatter)

        # change log handler to custom
        logger.removeHandler(logger.handlers[0])
        logger.addHandler(char_handler)

        # start process in another thread
        process = subprocess.Popen(args, buffsize, executable, stdin, stdout, stderr, preexec_fn,
                                   close_fds, shell, cwd, env, None, startupinfo, creationflags,
                                   restore_signals, start_new_session, pass_fds, encoding=encoding,
                                   errors=errors)

        # set read as non blocking
        flags = fcntl(process.stdout, F_GETFL)
        fcntl(process.stdout, F_SETFL, flags | O_NONBLOCK)

        back_up = bytearray()
        before = time.time()
        while process.poll() is None:
            while True:
                if time.time() - before > timeout:
                    process.terminate()
                    raise TimeoutError
                # peek will not work
                if stdout == ProcessCommunicable.PIPE:
                    output = process.stdout.read(1)
                elif stderr == ProcessCommunicable.PIPE:
                    output = process.stderr.read(1)

                if output:
                    before = time.time()
                    back_up += output
                    logger.info(output.decode())
                else:
                    break

        # replace original stream by our backup
        fake_buffered_reader = io.BufferedReader(io.BytesIO(back_up))
        if stdout == ProcessCommunicable.PIPE:
            process.stdout = fake_buffered_reader
        elif stderr == ProcessCommunicable.PIPE:
            process.stderr = fake_buffered_reader

        # return logger to original state
        logger.removeHandler(char_handler)
        logger.addHandler(logger_bckup)

        return process

    @staticmethod
    def run_logging(args, timeout=None, buffsize=-1, executable=None, stdin=None, stdout=None,
                    stderr=None, preexec_fn=None, close_fds=True, shell=False, cwd=None,
                    env=None, universal_newlines=None, startupinfo=None, creationflags=0,
                    restore_signals=True, start_new_session=False, pass_fds=(),
                    encoding=None, errors=None):
        '''
        Creates subprocess and logs it outputs
        ! output stream is replaced with copy !
        '''

        logger = logging.getLogger('brest')

        # start subprocess
        process = subprocess.Popen(args, buffsize, executable, stdin, stdout, stderr, preexec_fn,
                                   close_fds, shell, cwd, env, universal_newlines, startupinfo, creationflags,
                                   restore_signals, start_new_session, pass_fds, encoding=encoding,
                                   errors=errors)
        # wait for it to finish
        process.wait(timeout)

        if stdout == ProcessCommunicable.PIPE:
            output = process.stdout.read()
        elif stderr == ProcessCommunicable.PIPE:
            output = process.stderr.read()

        # log program output
        logger.info(output.decode())

        # replace original stream with fake one
        backup = bytearray()
        backup += output
        fake_buffered_reader = io.BufferedReader(io.BytesIO(backup))

        if stdout == ProcessCommunicable.PIPE:
            process.stdout = fake_buffered_reader
        elif stderr == ProcessCommunicable.PIPE:
            process.stderr = fake_buffered_reader

        return process
