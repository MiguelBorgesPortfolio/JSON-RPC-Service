"""
 Simple JSON-RPC Client

"""
import json
import socket

class JSONRPCClient:
    """The JSON-RPC client."""

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None
        self.ID = 0
        self.connect()  # (3) Reutilização de ligações TCP/IP

    def connect(self):
        """Connects to the server."""
        if self.sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))

    def close(self):
        """Closes the connection."""
        if self.sock:
            self.sock.close()
            self.sock = None

    def send(self, msg):
        """Sends a message to the server."""
        self.connect()  # (3) Reutilização de ligações TCP/IP
        self.sock.sendall(msg.encode())
        return self.sock.recv(4096).decode()  # Increased buffer size for larger responses

    def invoke(self, method, params):
        """Invokes a remote function."""
        self.ID += 1
        req = {
            'id': self.ID,
            'jsonrpc': '2.0',
            'method': method,
            'params': params
        }
        msg = self.send(json.dumps(req))
        res = json.loads(msg)
        if 'error' in res:
            error_code = res['error'].get('code')
            error_message = res['error'].get('message', 'Unknown error')
            if error_code == -32601:  # Method not found
                raise AttributeError(error_message)
            else:
                raise TypeError(error_message)
        return res['result']

    def invoke_batch(self, requests):
        """Sends a batch of requests."""
        for req in requests:
            self.ID += 1
            req['id'] = self.ID
            req['jsonrpc'] = '2.0'
        msg = self.send(json.dumps(requests))
        responses = json.loads(msg)
        return responses

    def __getattr__(self, name):
        """Invokes a generic function."""
        # (1) Parâmetros com nome (named parameters)
        def inner(*params, **named_params):
            if named_params:
                return self.invoke(name, named_params)
            return self.invoke(name, params)

        return inner


if __name__ == "__main__":
    client = JSONRPCClient('127.0.0.1', 8000)
    try:

        # Test batch request
        print("\nTesting batch request:")
        batch_requests = [
            {"method": "hello", "params": []},
            {"method": "add", "params": [1, 2]},
            {"method": "mul", "params": [2, 3]}
        ]
        batch_responses = client.invoke_batch(batch_requests)
        # (2) Várias funções num único pedido (batch)
        for response in batch_responses:
            print(response)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()
