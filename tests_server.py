"""
 JSON-RPC Tests

"""

import json
import random
import socket
import string
import time
import threading
import unittest

import functions
from server import JSONRPCServer


# Define server host and port
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 8000


class TestBase(unittest.TestCase):
    """Base for all tests."""

    def setUp(self):
        # Initiate the server
        self.server = JSONRPCServer(SERVER_HOST, SERVER_PORT)

        # Register functions
        self.server.register('hello', functions.hello)
        self.server.register('greet', functions.greet)
        self.server.register('add', functions.add)
        self.server.register('sub', functions.sub)
        self.server.register('mul', functions.mul)
        self.server.register('div', functions.div)

        # Start the server in a thread
        self.server_thread = threading.Thread(target=self.server.start)
        self.server_thread.start()

        # Starts the client
        time.sleep(0.001)
        self.sock = socket.socket()
        self.sock.connect((SERVER_HOST, SERVER_PORT))

    def tearDown(self):
        self.server.stop()
        self.server_thread.join()
        self.sock.close()

    def send(self, msg):
        """Sends a message to the socket"""
        self.sock.sendall(msg.encode())
        res = self.sock.recv(1024).decode()
        return res

    def send_json(self, payload):
        """Sends json message to the socket."""
        msg = json.dumps(payload)
        res = self.send(msg)
        return json.loads(res)

    def jsonrpc_req(self, id, method, params):
        """Sends a json-rpc request."""
        req = {
            'id': id,
            'jsonrpc': '2.0',
            'method': method,
            'params': params
        }
        return self.send_json(req)


class TestProtocolFields(TestBase):
    """Tests the JSON-RPC protocol."""

    def test_version(self):
        """JSON-RPC must return the protocol."""
        res = self.jsonrpc_req(1, 'hello', [])
        self.assertEqual(res['jsonrpc'], '2.0')

    def test_id(self):
        """JSON-RPC must return the same id."""
        rpcid = random.randint(1, 10)
        res = self.jsonrpc_req(rpcid, 'hello', [])
        self.assertEqual(res['id'], rpcid)

    def test_result(self):
        """JSON-RPC must return the result."""
        res = self.jsonrpc_req(1, 'hello', [])
        self.assertIn('result', res)
        self.assertNotIn('error', res)

    def test_error(self):
        """JSON-RPC must return the error."""
        res = self.jsonrpc_req(1, 'nofunc', [])
        self.assertIn('error', res)
        self.assertNotIn('result', res)


class TestResults(TestBase):
    """Tests the functions results."""

    def test_hello(self):
        """Function must return correct result."""
        res = self.jsonrpc_req(1, 'hello', [])
        self.assertEqual(res['result'], 'Hi!')

    def test_greet(self):
        """Function must return correct result."""
        res = self.jsonrpc_req(1, 'greet', ['John Doe'])
        self.assertEqual(res['result'], 'Hello John Doe')

    def test_add(self):
        """Function must return correct result."""
        res = self.jsonrpc_req(1, 'add', [4, 2])
        self.assertEqual(res['result'], 6)

    def test_sub(self):
        """Function must return correct result."""
        res = self.jsonrpc_req(1, 'sub', [4, 2])
        self.assertEqual(res['result'], 2)

    def test_mul(self):
        """Function must return correct result."""
        res = self.jsonrpc_req(1, 'mul', [4, 2])
        self.assertEqual(res['result'], 8)

    def test_div(self):
        """Function must return correct result."""
        res = self.jsonrpc_req(1, 'div', [6, 2])
        self.assertEqual(res['result'], 3)


class TestRegisteredFunctions(TestBase):
    """Tests functions registered dynamically."""

    def test_new_function(self):
        """Server must register new functions."""
        # Register new function
        def square(num):
            return num * num
        self.server.register('square', square)

        res = self.jsonrpc_req(1, 'square', [2])
        self.assertEqual(res['result'], 4)

    def test_random_function(self):
        """Server must register new functions."""
        # Register new function
        def random_function(num):
            return num

        # Generate and register with random name
        name = ''.join(random.sample(string.ascii_lowercase, 10))
        self.server.register(name, random_function)

        res = self.jsonrpc_req(1, name, [2])
        self.assertEqual(res['result'], 2)


class TestErrors(TestBase):
    """Tests errors."""

    def testErrorFields(self):
        """Errors must return code and message."""
        res = self.jsonrpc_req(1, 'nofunc', [])
        self.assertIn('code', res['error'])
        self.assertIn('message', res['error'])

    def testProtocolFields(self):
        """Errors must still return the id and jsonrpc fields."""
        res = self.jsonrpc_req(1, 'nofunc', [])
        self.assertIn('id', res)
        self.assertIn('jsonrpc', res)

    def testMethodNotFound(self):
        """Tests a specific error."""
        res = self.jsonrpc_req(1, 'nofunc', [])
        self.assertEqual(res['error']['code'], -32601)
        self.assertEqual(res['error']['message'], 'Method not found')

    def testInvalidParams(self):
        """Tests a specific error."""
        res = self.jsonrpc_req(1, 'greet', [])
        self.assertEqual(res['error']['code'], -32602)
        self.assertEqual(res['error']['message'], 'Invalid params')

    def testInvalidRequest(self):
        """Tests a specific error."""
        res = self.send_json({'error': 'this is valid json'})
        self.assertEqual(res['error']['code'], -32600)
        self.assertEqual(res['error']['message'], 'Invalid Request')

    def testParseError(self):
        """Tests a specific error."""
        res = self.send('This is invalid json')
        res = json.loads(res)
        self.assertEqual(res['error']['code'], -32700)
        self.assertEqual(res['error']['message'], 'Parse error')


class TestEdgeCases(TestBase):
    """Tests some edge cases."""

    def testNoParams(self):
        """JSON-RPC params may be omitted if not needed."""
        req = {
            'id': 1,
            'jsonrpc': '2.0',
            'method': 'hello',
        }
        res = self.send_json(req)
        self.assertEqual(res['result'], 'Hi!')

    def testNoParamsNeeded(self):
        """JSON-RPC params cannot be omitted if needed."""
        req = {
            'id': 1,
            'jsonrpc': '2.0',
            'method': 'greet',
        }
        res = self.send_json(req)
        self.assertEqual(res['error']['code'], -32602)
        self.assertEqual(res['error']['message'], 'Invalid params')

    def testNotifications(self):
        """JSON-RPC notifications dont have IDs and server must not respond."""
        req = {
            'jsonrpc': '2.0',
            'method': 'greet',
        }
        msg = json.dumps(req)
        self.sock.sendall(msg.encode())
        time.sleep(0.1)
        res = self.sock.recv(1024).decode()
        self.assertEqual(res, '')
###
class TestNewErrors(TestBase):
    """Tests extras."""
    def test_zero_division_error(self):
        """Tests division by zero error."""
        res = self.jsonrpc_req(1, 'div', [1, 0])
        self.assertEqual(res['error']['code'], -32001)
        # Verifica se o código de erro corresponde a divisão por zero
        self.assertEqual(res['error']['message'], 'Division by zero')
        # Verifica se a mensagem de erro é correta

    def test_missing_method(self):
        """Tests request missing the method field."""
        req = {
            'id': 1,
            'jsonrpc': '2.0'
        }
        res = self.send_json(req)
        self.assertEqual(res['error']['code'], -32600)
        # Verifica se o código de erro corresponde a uma solicitação inválida
        self.assertEqual(res['error']['message'], 'Invalid Request')
        # Verifica se a mensagem de erro é correta

    def test_invalid_json(self):
        """Tests sending completely invalid JSON."""
        res = self.send('{ invalid json }')
        res = json.loads(res)
        self.assertEqual(res['error']['code'], -32700)
        # Verifica se o código de erro corresponde a um erro de análise JSON inválido
        self.assertEqual(res['error']['message'], 'Parse error')
        # Verifica se a mensagem de erro é correta

    def test_empty_request(self):
        """Tests sending an empty request."""
        res = self.send_json({})
        self.assertEqual(res['error']['code'], -32600)
        # Verifica se o código de erro corresponde a uma solicitação inválida
        self.assertEqual(res['error']['message'], 'Invalid Request')
        # Verifica se a mensagem de erro é correta

    def test_method_invalid_type(self):
        """Tests sending a method name that is not a string."""
        req = {
            'id': 1,
            'jsonrpc': '2.0',
            'method': 123,
            'params': []
        }
        res = self.send_json(req)
        self.assertEqual(res['error']['code'], -32600)
        # Verifica se o código de erro corresponde a uma solicitação inválida
        self.assertEqual(res['error']['message'], 'Invalid Request')
        # Verifica se a mensagem de erro é correta

    def test_params_invalid_type(self):
        """Tests sending params that are not an array or object."""
        req = {
            'id': 1,
            'jsonrpc': '2.0',
            'method': 'add',
            'params': 'invalid params'
        }
        res = self.send_json(req)
        self.assertEqual(res['error']['code'], -32602)
        # Verifica se o código de erro corresponde a parâmetros inválidos
        self.assertEqual(res['error']['message'], 'Invalid params')
        # Verifica se a mensagem de erro é correta
