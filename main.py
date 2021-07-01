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

def receive_opponent_piece(piece):
    return json.dumps({"type": "receive_opponent_piece", "piece": piece})

# EVENTS

async def enter_game(game_id, player):
    """ TODO fix asssumption that there will only be two players per game """
    # if game does not exist, create it
    if game_id not in GAMES:
        GAMES[game_id] = create_game(game_id, player)
        message = wait_for_opponent_response()
        await player.send(message)
    # if game exists, add player to game if they are not already in it    
    elif player.remote_address[0] not in map(lambda p: p.remote_address[0], GAMES[game_id]["players"]):
        GAMES[game_id]["players"].append(player)
        message = start_game_response()
        await asyncio.wait([player.send(message) for player in GAMES[game_id]["players"]])
    else:
        print("Already in game...")

async def send_piece(game_id, player, piece):
    # make sure game exists
    if game_id not in GAMES:
        print("Game does not exist...")
        return

    # get opponent player and send piece to opponent player
    await get_opponent_player(game_id, player.remote_address[0])\
        .send(receive_opponent_piece(piece))

async def exit_game(player_remote_address):
    # get game with player that is disconnecting
    result = list(filter(lambda g: player_remote_address in map(lambda p: p.remote_address[0], g["players"]), GAMES.values()))
    game_with_player = result[0] if len(result) > 0 else None

    # if game exists, delete game and remove opponent player from game
    if game_with_player:
        del GAMES[game_with_player["game_id"]]

        # remove opponent player from game
        result = list(filter(lambda p: p.remote_address[0] != player_remote_address, game_with_player["players"]))
        opponent_player = result[0] if len(result) > 0 else None
        if opponent_player:
            message = exit_game_response()
            await opponent_player.send(message)

# --------------------------

# HELPER FUNCTIONS

def get_opponent_player(game_id, player_remote_address):
    opponent_player = list(filter(lambda p: p.remote_address[0] != player_remote_address, GAMES[game_id]["players"]))[0];
    return opponent_player    

def create_game(game_id, player=None):
    print("Creating game...")
    return {"players": ([player] if player else []), "game_id": game_id}

# --------------------------

async def init(websocket, path):
    try:
        async for message in websocket:
            data = json.loads(message)
            if data["action"] == "enter_game":
                await enter_game(data["gameId"], websocket)
            elif data["action"] == "send_piece":
                await send_piece(data["gameId"], websocket, data["piece"])
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