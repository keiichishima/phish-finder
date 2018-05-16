#!/usr/bin/env python

from websocket_server import WebsocketServer

_clients = {}

def _new_client(_client, _server):
    print(_client['id'], 'arrived')
    _clients[_client['id']] = _client

def _client_left(_client, _server):
    print(_client['id'], 'left')
    del _clients[_client['id']]

def _message_received(_client, _server, _msg):
    for _id in _clients.keys():
        if _id == _client['id']:
            continue
        _server.send_message(_clients[_id], _msg)

_server = WebsocketServer(5678, '127.0.0.1')
_server.set_fn_new_client(_new_client)
_server.set_fn_client_left(_client_left)
_server.set_fn_message_received(_message_received)
_server.run_forever()
