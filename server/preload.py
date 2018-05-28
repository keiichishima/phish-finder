#!/usr/bin/env python

import argparse
import json
import os

import websocket

_ws = websocket.create_connection('ws://127.0.0.1:5678')

_parser = argparse.ArgumentParser()
_parser.add_argument('-r',
                     dest='root',
                     required=True,
                     help='preload root directory')
_args = _parser.parse_args()

for _root, _dirs, _filenames in os.walk(_args.root):
    _filepaths = [os.path.join(_root, _filename)
                  for _filename in _filenames]

for _filepath in _filepaths:
    with open(_filepath, 'r') as _f:
        for _line in _f:
            _ws.send(_line.rstrip())
