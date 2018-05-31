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

if __name__ == '__main__':
    import argparse

    _parser = argparse.ArgumentParser()
    _parser.add_argument('-b',
                         dest='bind_address',
                         default='127.0.0.1',
                         help='Bind address ("-b all" for wildcard')
    _args = _parser.parse_args()

    if _args.bind_address == 'all':
        _args.bind_address = ''

    _server = WebsocketServer(5678, _args.bind_address)
    _server.set_fn_new_client(_new_client)
    _server.set_fn_client_left(_client_left)
    _server.set_fn_message_received(_message_received)
    _server.run_forever()
