#!/usr/bin/env python

import asyncio
import os
import json

import websockets

GAMES = {}
# EVENT RESPONSES

def wait_for_opponent_response():
    return json.dumps({"type": "wait_for_opponent"})

def start_game_response():
    return json.dumps({"type": "start_game"})

def exit_game_response():
    return json.dumps({"type": "exit_game"})

# EVENTS

async def enter_game(game_id, player_web_socket):
    """ TODO fix asssumption that there will only be two players per game """
    # if game does not exist, create it
    if game_id not in GAMES:
        GAMES[game_id] = {"players": [player_web_socket], "game_id": game_id}
        message = wait_for_opponent_response()
        await player_web_socket.send(message)
    # if game exists, add player to game if they are not already in it    
    elif player_web_socket.remote_address[0] not in map(lambda p: p.remote_address[0], GAMES[game_id]["players"]):
        GAMES[game_id]["players"].append(player_web_socket)
        message = start_game_response()
        await asyncio.wait([player.send(message) for player in GAMES[game_id]["players"]])
    else:
        print("Already in game...")

async def exit_game(player_remote_address):
    # get game with player that is disconnecting
    result = list(filter(lambda g: player_remote_address in map(lambda p: p.remote_address[0], g["players"]), GAMES.values()))

    # if game exists, delete game and remove opponent player from game
    if len(result):
        game_with_player = result[0]
        del GAMES[game_with_player["game_id"]]

        # remove opponent player from game
        result = list(filter(lambda p: p.remote_address[0] != player_remote_address, game_with_player["players"]))
        if len(result):
            opponent_player = result[0]
            message = exit_game_response()
            await opponent_player.send(message)

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
        print("Exiting game...")
        await exit_game(websocket.remote_address[0])
        print("Connection closed...")

start_server = websockets.serve(init, "", 5001)
#start_server = websockets.serve(init, "localhost", 5001)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()