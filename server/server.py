#!/usr/bin/env python

import asyncio
from datetime import datetime

import websockets

async def _server(websocket, path):
    while True:
        now = datetime.utcnow().isoformat() + 'Z'
        await websocket.send(now)
        await asyncio.sleep(5)

_start_server = websockets.serve(_server, '127.0.0.1', 5678)
_loop = asyncio.get_event_loop()
_loop.run_until_complete(_start_server)
_loop.run_forever()
