import json
import requests
from typing import List
from fastapi import HTTPException, Depends
from models import *
from user import *

json_folder = "data"
json_filename_user = "user"
json_filename_rollcall = "rollcall"

def load_json(filename):
    with open(f"{json_folder}/{filename}.json","r") as f:
        data = json.load(f)[filename]
    return data

def save_json(filename, data):
    with open(f"{json_folder}/{filename}.json", 'w') as f:
        json.dump({filename: data}, f)


link = 'https://tubes-tst-18221066-rollcall.azurewebsites.net/'

def get_token():
    token_link = link + '/token'
    token_response = requests.post(token_link, data={'username': 'matchup', 'password': 'matchup'})
    token = token_response.json().get('access_token')
    return token


def get_user_rollcall():
    headers = {'Authorization': f'Bearer {get_token()}'}
    user_response = requests.get(link + 'user/', headers=headers)
    return user_response.json() 


def add_boardgame(user_name: str, boardgame_id: int):
    rollcall = load_json(json_filename_rollcall)
    user = next((user for user in rollcall if user['UserName'] == user_name), None)
    if user is None:
        user = {'UserName': user_name, 'Boardgame': [boardgame_id]}
        rollcall.append(user)
    else:
        if boardgame_id not in user['Boardgame']:
            user['Boardgame'].append(boardgame_id)
    save_json(json_filename_rollcall, rollcall)
    return rollcall

def remove_boardgame(user_name: str, boardgame_id: int):
    rollcall = load_json(json_filename_rollcall)
    user = next((user for user in rollcall if user['UserName'] == user_name), None)
    if user is not None and boardgame_id in user['Boardgame']:
        user['Boardgame'].remove(boardgame_id)
    save_json(json_filename_rollcall, rollcall)
    return rollcall


# Matchmaking
def matchmaking(username: str):
    rollcall = load_json(json_filename_rollcall)
    matched_users = []
    for user in rollcall:
        if any(boardgame in username for boardgame in user['boardgame']):
            # Remove the password from the user data
            user_without_password = {key: value for key, value in user.items() if key != 'password'}
            matched_users.append(user_without_password)
    return matched_users

def matchmaking_rollcall(username):
    rollcall_users = load_json('rollcall')
    user_boardgames = next((user['Boardgame'] for user in rollcall_users if user['UserName'] == username), None)
    
    if user_boardgames is None:
        return f"Error: Pengguna {username} tidak memiliki preferensi boardgame"
    
    user_rollcall = get_user_rollcall()
    
    matched_users = []
    for user in user_rollcall:
        if user['username'] != username and any(game in user_boardgames for game in user['boardgame']):
            user_without_password = {key: value for key, value in user.items() if key != 'password'}
            matched_users.append(user_without_password)
    
    return matched_users
