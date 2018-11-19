import logging
import time
import json
import socket
from ..util import Password

logging.basicConfig(format='[%(asctime)s] - %(levelname)s - %(message)s', level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

class AgentBase(object):
    """Cross-platform agent used to validate requests and control
       sockets for communication to mothership"""

    def __init__(self, signing_key):

        # If AgentBase is subclassed, this will call __init__ for
        # the next class in MRO of extending class. Otherwise, it
        # is equivalent to object.__init__()
        super().__init__()

        self.used_hash = []
        self.signing_key = signing_key
        self.sock = None

    def validate_message(self, request_string):

        try:
            request = json.loads(request_string)
        except Exception as exc:
            raise Exception('Request is not valid JSON')

        tmp_request = {}

        for key in request:
            if key != 'signature':
                tmp_request[key] = request[key]

        LOGGER.debug('TMP_REQUEST: %s' % tmp_request)
        json_tmp = json.dumps(tmp_request, sort_keys=True)
        sign_string = '%s::%s' % (json_tmp, self.signing_key)

        pw = Password()
        if not pw.auth_check(sign_string, request['signature']):
            raise Exception('Signature validation failed')

        if request['signature'] in self.used_hash:
            raise Exception('Request expired')

        return True

    def sign_request(self, request_data):

        request_data['timestamp'] = time.time()
        request_string = json.dumps(request_data, sort_keys=True)

        pw = Password()

        sign_string = '%s::%s' % (request_string, self.signing_key)
        signature = pw.make_hash(sign_string)

        request_data['signature'] = signature

        return request_data

    def start_listener(self, ip='0.0.0.0', port=1337):

        LOGGER.debug('Starting listener on %s:%s' % (ip, port))

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((ip, port))
            sock.listen(5)

            while True:

                (c_sock, c_ip) = sock.accept()
                c_msg = c_sock.recv(4096).decode('utf8')

                if c_msg:
                    LOGGER.debug('C_SOCK: %s' % c_sock)
                    LOGGER.debug('C_IP: %s:%s' % c_ip)
                    LOGGER.debug('C_MSG: %s' % c_msg)
                    response = self.process_request(c_msg)
                    try:
                        self.send_response(response, c_sock)
                    except Exception as exc:
                        LOGGER.error('Failed sending response: %s' % exc)

    def process_request(self, message):

        try:
            valid = self.validate_message(message)
        except Exception as exc:
            response = {'status': 'error', 'message': '%s' % exc}

        if valid:
            request_data = json.loads(message)

            try:
                response = self.execute_request(request_data)
            except Exception as exc:
                response = {'status': 'error', 'message': '%s' % exc}

        signed_response = json.dumps(self.sign_request(response))
        return signed_response

    def execute_request(self, request_data):

        cmd_lookup = {'start_service': self.start_service,
                      'restart_service': self.restart_service,
                      'stop_service': self.stop_service,
                      'list_processes': self.list_processes}

        LOGGER.debug('REQUEST: %s' % request_data)

        if 'args' in request_data and request_data['args']:
            args = request_data['args']
        else:
            args = []

        try:
            cmd_lookup[request_data['command']](*args)
        except Exception as exc:
            return {'status': 'error', 'message': '%s' % exc}

        response = {'status': 'success', 'raw_output': self.stdout}

        return response

    def send_response(self, message, sock):
        sock.send(message.encode())
        
    def start_service(self, service_name):
        raise NotImplementedError

    def restart_service(self, service_name):
        raise NotImplementedError

    def stop_service(self, service_name):
        raise NotImplementedError

    def list_processes(self):
        raise NotImplementedError
