import subprocess

class CLI(object):

    def __init__(self, timeout=45):

        self.timeout = timeout
        self.cmd = None
        self.stdout = None
        self.stderr = None
        self.exitcode = None

    def shell_exec(self, *args):

        args = [str(x) for x in args]

        # https://docs.python.org/3/library/subprocess.html#security-considerations
        #
        # Unlike some other popen functions, this implementation will never implicitly call
        # a system shell. This means that all characters, including shell metacharacters, 
        # can safely be passed to child processes. If the shell is invoked explicitly, 
        # via shell=True, it is the application’s responsibility to ensure that all whitespace
        # and metacharacters are quoted appropriately to avoid shell injection vulnerabilities.
        self.cmd = ' '.join(args)
        try:
            pull = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except FileNotFoundError as e:
            raise Exception('Invalid command')

        try:
            (stdout, stderr) = pull.communicate(timeout=self.timeout)
            stdout = stdout.decode('ascii')
            stderr = stderr.decode('ascii')
            returncode = pull.returncode
        except Exception as e:

            # Attempt to kill running process, fails for command that was run with sudo
            try:
                pull.kill()
            except PermissionError as exc:

                # That failed, try one more time, hopefully kill is in sudoers command list
                try:
                    status = self.shell_exec('/usr/bin/sudo', '/usr/bin/kill', '-9', pull.pid)
                except Exception as ex2:
                    raise Exception('Process timeout expired, all attempts to kill PID %s failed' % pull.pid)
                else:
                    if status != 0:
                        raise Exception('Process timeout expired, all attempts to kill PID %s failed' % pull.pid)
                    else:
                        raise Exception('kill -9 success: %s ' % e)
            else:
                raise Exception('pull.kill() success: %s' % e)

        self.stdout, self.stderr, self.returncode = (stdout, stderr, returncode)
        return self.returncode

    def shell_exec_bg(self, *args):

        self.cmd = ' '.join(args)
        try:
            pull = subprocess.Popen(args)
        except FileNotFoundError as e:
            raise Exception('Invalid command')

        return True
