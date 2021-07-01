#!/usr/bin/env python

import asyncio
import os
import json

import websockets

GAMES = {}

# EVENT RESPONSES

def wait_for_player_response():
    return json.dump({"type": "wait_for_player"})

def start_game_response():
    return json.dump({"type": "start_game"})

# EVENTS

async def enter_game(game_id, player_web_socket):
    # TODO fix asssumption that there will only be two players per game
    if game_id not in GAMES:
        GAMES[game_id] = {'players': [player_web_socket], 'game_id': game_id}
        message = wait_for_player_response()
        await player_web_socket.send(message)
    else:
        GAMES[game_id]['players'].append(player_web_socket)
        message = start_game_response()
        await asyncio.wait([player.send(message) for player in GAMES[game_id]['players']])
        
# --------------------------

async def init(websocket, path):
    try:
        async for message in websocket:
            data = json.loads(message)
            if data["action"] == "enter_game":
                await enter_game(data["gameId"], websocket)
            else:
                print("Unsupported action...")
    finally:
        print("Connection closed...")

#start_server = websockets.serve(init, "", int(os.environ["PORT"]))
start_server = websockets.serve(init, "localhost", 5001)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()