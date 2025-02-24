"""
 Simple JSON-RPC Server

"""
import json
import socket
import threading

import functions

class JSONRPCServer:
    """The JSON-RPC server."""

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None
        self.funcs = {}

    def register(self, name, function):
        """Registers a function."""
        self.funcs[name] = function

    def start(self):
        """Starts the server."""
        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)  # Allow up to 5 connections in the queue
        print(f'Listening on port {self.port} ...')

        try:
            while True:
                # Accepts and handles client
                conn, addr = self.sock.accept()
                print(f'Connected by {addr}')
                client_thread = threading.Thread(target=self.handle_client, args=(conn,))
                client_thread.daemon = True
                # Threads dos clientes são definidas como
                # daemons para terminar com o programa principal
                client_thread.start()

        except ConnectionAbortedError:
            pass
        except OSError:
            pass

    def stop(self):
        """Stops the server."""
        self.sock.close()

    def handle_client(self, conn):
        """Handles the client connection."""
        try:
            # Receive message
            msg = conn.recv(1024).decode()
            print('Received:', msg)

            try:
                req = json.loads(msg)
                if isinstance(req, list):  # (2) Várias funções num único pedido (batch)
                    res = [self.process_request(r) for r in req]
                else:
                    res = self.process_request(req)

                if res is not None:
                    res = json.dumps(res)
                    conn.send(res.encode())

            except json.JSONDecodeError:
                res = {
                    'jsonrpc': '2.0',
                    'id': None,
                    'error': {
                        'code': -32700,
                        'message': 'Parse error'
                    }
                }
                conn.send(json.dumps(res).encode())

        finally:
            conn.close()

    def process_request(self, req):
        """Processes a single JSON-RPC request."""
        try:
            if not isinstance(req, dict) or 'jsonrpc' not in req or 'method' not in req:
                raise ValueError("Invalid Request")

            method = req.get('method')
            params = req.get('params', [])
            req_id = req.get('id', None)

            if not isinstance(method, str):
                if req_id is not None:
                    return {
                        'jsonrpc': '2.0',
                        'id': req_id,
                        'error': {
                            'code': -32600,
                            'message': 'Invalid Request'
                        }
                    }
            elif method not in self.funcs:
                if req_id is not None:
                    return {
                        'jsonrpc': '2.0',
                        'id': req_id,
                        'error': {
                            'code': -32601,
                            'message': 'Method not found'
                        }
                    }
            else:
                try:
                    # Check if params is a dictionary  # (1) Parâmetros com nome (named parameters)
                    if isinstance(params, dict):
                        result = self.funcs[method](**params)
                    else:
                        result = self.funcs[method](*params)

                    if req_id is not None:
                        return {
                            'jsonrpc': '2.0',
                            'id': req_id,
                            'result': result
                        }
                except TypeError:
                    if req_id is not None:
                        return {
                            'jsonrpc': '2.0',
                            'id': req_id,
                            'error': {
                                'code': -32602,
                                'message': 'Invalid params'
                            }
                        }
                except ZeroDivisionError:
                    if req_id is not None:
                        return {
                            'jsonrpc': '2.0',
                            'id': req_id,
                            'error': {
                                'code': -32001,
                                'message': 'Division by zero'
                            }
                        }
                except Exception as e:
                    if req_id is not None:
                        return {
                            'jsonrpc': '2.0',
                            'id': req_id,
                            'error': {
                                'code': -32603,
                                'message': str(e)
                            }
                        }
        except json.JSONDecodeError:
            return {
                'jsonrpc': '2.0',
                'id': None,
                'error': {
                    'code': -32700,
                    'message': 'Parse error'
                }
            }
        except ValueError:
            return {
                'jsonrpc': '2.0',
                'id': None,
                'error': {
                    'code': -32600,
                    'message': 'Invalid Request'
                }
            }
        return None


if __name__ == "__main__":
    # Test the JSONRPCServer class
    server = JSONRPCServer('0.0.0.0', 8000)

    # Register functions
    server.register('hello', functions.hello)
    server.register('greet', functions.greet)
    server.register('add', functions.add)
    server.register('sub', functions.sub)
    server.register('mul', functions.mul)
    server.register('div', functions.div)
    server.register('add3', functions.add3)

    # Start the server
    server.start()
