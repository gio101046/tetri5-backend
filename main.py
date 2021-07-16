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

def receive_piece(piece):
    return json.dumps({"type": "receive_piece", "piece": piece})

def receive_stack(stack):
    return json.dumps({"type": "receive_stack", "stack": stack})

def receive_stats(stats):
    return json.dumps({"type": "receive_stats", "stats": stats})

# EVENTS

async def enter_game(game_id, client_id, player):
    """ TODO fix asssumption that there will only be two players per game """
    # if game does not exist, create it
    if game_id not in GAMES:
        GAMES[game_id] = create_game(game_id, client_id, player)
        await player.send(wait_for_opponent_response())
    # if game exists, add player to game if they are not already in it    
    elif client_id not in GAMES[game_id]["clients"]:
        GAMES[game_id]["players"].append(player)
        GAMES[game_id]["clients"].append(client_id)
        await asyncio.wait([player.send(start_game_response()) for player in GAMES[game_id]["players"]])
    else:
        print("Already in game...")

async def send_piece(game_id, client_id, player, piece):
    # make sure game exists
    if game_id not in GAMES:
        print("Game does not exist...")
        return

    # get opponent player and send piece to opponent player
    await get_opponent_player(game_id, player)\
        .send(receive_piece(piece))

async def send_stack(game_id, client_id, player, stack):
    # make sure game exists
    if game_id not in GAMES:
        print("Game does not exist...")
        return

    # get opponent player and send piece to opponent player
    await get_opponent_player(game_id, player)\
        .send(receive_stack(stack))

async def send_stats(game_id, client_id, player, stats):
    # make sure game exists
    if game_id not in GAMES:
        print("Game does not exist...")
        return

    # get opponent player and send piece to opponent player
    await get_opponent_player(game_id, player)\
        .send(receive_stats(stats))

# TODO refactor function
async def exit_game(player_remote_address):
    # get game with player that is disconnecting
    result = list(filter(lambda g: player_remote_address in map(lambda p: p.remote_address[0], g["players"]), GAMES.values()))
    game_with_player = result[0] if result else None

    # if game exists, delete game and remove opponent player from game
    if game_with_player:
        del GAMES[game_with_player["game_id"]]

        # remove opponent player from game
        result = list(filter(lambda p: p.remote_address[0] != player_remote_address, game_with_player["players"]))
        opponent_player = result[0] if result else None
        if opponent_player:
            message = exit_game_response()
            await opponent_player.send(message)

# --------------------------

# HELPER FUNCTIONS

def get_opponent_player(game_id, player):
    return list(filter(lambda p: p != player, GAMES[game_id]["players"]))[0]    

def create_game(game_id, client_id=None, player=None):
    return {"players": ([player] if player else []),\
            "clients": ([client_id] if client_id else []),\
            "game_id": game_id}

# --------------------------

async def init(websocket, path):
    try:
        async for message in websocket:
                if message == "ping": # prevents client from timing out if waiting for opponent
                    await websocket.send("pong");
                else:
                    data = json.loads(message)
                    if data["action"] == "enter_game":
                        await enter_game(data["gameId"], data["clientId"], websocket)
                    elif data["action"] == "send_piece":
                        await send_piece(data["gameId"], data["clientId"], websocket, data["piece"])
                    elif data["action"] == "send_stack":
                        await send_stack(data["gameId"], data["clientId"], websocket, data["stack"])
                    elif data["action"] == "send_stats":
                        await send_stats(data["gameId"], data["clientId"], websocket, data["stats"])
                    else:
                        print("Unsupported action...")
    finally:
        print("Exiting game...")
        await exit_game(websocket.remote_address[0])
        print("Connection closed...")

start_server = websockets.serve(init, "", int(os.environ["PORT"]), ping_interval=None)
#start_server = websockets.serve(init, "localhost", 5001, ping_interval=None)
# ping_interval=None is important, otherwise the client will disconnect
# https://stackoverflow.com/a/58993145/11512104

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()