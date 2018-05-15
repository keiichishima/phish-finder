#!/usr/bin/env python

import asyncio
from datetime import datetime

import websockets

async def _server(websocket, path):
    with open('test.txt', 'r') as _f:
        _f.seek(0, 2)
        while True:
            _cur = _f.tell()
            _line = _f.readline()
            if not _line:
                _f.seek(_cur)
                await asyncio.sleep(1)
            else:
                await websocket.send(_line)


_start_server = websockets.serve(_server, '127.0.0.1', 5678)
_loop = asyncio.get_event_loop()
_loop.run_until_complete(_start_server)
_loop.run_forever()
