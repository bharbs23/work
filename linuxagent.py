from .agentbase import AgentBase
from .cli import CLI
import logging

logging.basicConfig(format='[%(asctime)s] - %(levelname)s - %(message)s', level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

class LinuxAgent(AgentBase, CLI):

    def __init__(self, signing_key):

        super().__init__(signing_key)

    def start_service(self, service_name):

        cmd = ['/usr/bin/sudo', '/bin/systemctl', 'start', service_name]

        LOGGER.debug('Executing: %s' % cmd)
        self.shell_exec(*cmd)

        LOGGER.debug('STDOUT: %s' % self.stdout)
        LOGGER.debug('STDERR: %s' % self.stderr)

    def restart_service(self, service_name):

        cmd = ['/usr/bin/sudo', '/bin/systemctl', 'restart', service_name]

        LOGGER.debug('Executing: %s' % cmd)
        self.shell_exec(*cmd)

        LOGGER.debug('STDOUT: %s' % self.stdout)
        LOGGER.debug('STDERR: %s' % self.stderr)

    def stop_service(self, service_name):

        cmd = ['/usr/bin/sudo', '/bin/systemctl', 'stop', service_name]

        LOGGER.debug('Executing: %s' % cmd)
        self.shell_exec(*cmd)

        LOGGER.debug('STDOUT: %s' % self.stdout)
        LOGGER.debug('STDERR: %s' % self.stderr)

    def list_processes(self):

        cmd = ['/usr/bin/sudo', '/bin/systemctl', '--state=running']

        LOGGER.debug('Executing: %s' % cmd)
        self.shell_exec(*cmd)

        LOGGER.debug('STDOUT: %s' % self.stdout)
        LOGGER.debug('STDERR: %s' % self.stderr)
