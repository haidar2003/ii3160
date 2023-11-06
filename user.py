import json

from fastapi import HTTPException
from models import *

json_folder = "data"
json_filename_user = "user"
json_filename_sport = "sport"
json_filename_sport_preference = "sport_preference"

def load_json(filename):
    with open(f"{json_folder}/{filename}.json","r") as f:
        data = json.load(f)[filename]
    return data

def read_all_user() -> List[UserItemResponse]:
    user_data = load_json(json_filename_user)
    sport_data = load_json(json_filename_sport)
    sport_preference_data = load_json(json_filename_sport_preference)
    return [UserItemResponse(**{k: v for k, v in user.items() if k != 'Password'}, Sports=[sport['SportName'] for sport in sport_data if any(pref['UserID'] == user['UserID'] and pref['SportID'] == sport['SportID'] for pref in sport_preference_data)]) for user in user_data]

def read_user_by_username(username: str) -> UserItemResponse:
    user_data = next((item for item in load_json(json_filename_user) if item['UserName'] == username), None)
    sport_data = load_json(json_filename_sport)
    sport_preference_data = load_json(json_filename_sport_preference)

    if user_data is None:
        raise HTTPException(status_code=404, detail=f"User {username} not found")
    return UserItemResponse(**{k: v for k, v in user_data.items() if k != 'Password'}, Sports=[sport['SportName'] for sport in sport_data if any(pref['UserID'] == user_data['UserID'] and pref['SportID'] == sport['SportID'] for pref in sport_preference_data)])

def create_user(user_details: UserItem):
    user_data = load_json(json_filename_user)
    
    existing_usernames = set(item['UserName'] for item in user_data)
    if user_details.UserName in existing_usernames:
        raise HTTPException(status_code=400, detail=f"User {user_details.UserName} already exists")
    
    existing_id = set(item['UserID'] for item in user_data)

    user_id = 1
    while user_id in existing_id:
        user_id += 1
    
    new_user = {
        "UserID": user_id,
        "UserName": user_details.UserName,
        "UserEmail": user_details.UserEmail,
        "Password": user_details.Password,
        "Description": user_details.Description,
        "Province": user_details.Province,
        "City": user_details.City,
        "Street": user_details.Street,
        "DisplayName": user_details.DisplayName
    }

    user_data.append(new_user)

    with open(f'{json_folder}/{json_filename_user}.json', "w") as w:
            json.dump({f'{json_filename_user}': user_data}, w)
        
    return new_user


def update_user(username, password, updated_user: UserItemUpdate):
    user_data = load_json(json_filename_user)
    user = next((item for item in user_data if item['UserName'] == username), None)

    if user:
        if user['Password'] != password:
            raise HTTPException(status_code=400, detail="Wrong password")
        updated_fields = updated_user.dict(exclude_unset=True)
        user.update(updated_fields)
        with open(f'{json_folder}/{json_filename_user}.json', "w") as w:
            json.dump({f'{json_filename_user}': user_data}, w)
        return user
    else:
        raise HTTPException(status_code=404, detail=f"User {username} not found")
    
def delete_user(username, password):
    user_data = load_json(json_filename_user)
    sport_preference_data = load_json(json_filename_sport_preference)

    user_to_delete = next((item for item in user_data if item['UserName'] == username), None)
    
    if user_to_delete:
        if user_to_delete['Password'] != password:
            raise HTTPException(status_code=400, detail="Wrong password")
        
        user_data = [user for user in user_data if user['UserName'] != username]
        with open(f'{json_folder}/{json_filename_user}.json', "w") as w:
            json.dump({f'{json_filename_user}': user_data}, w)

        sport_preference_data = [pref for pref in sport_preference_data if pref['UserID'] != user_to_delete['UserID']]
        with open(f'{json_folder}/{json_filename_sport_preference}.json', "w") as w:
            json.dump({f'{json_filename_sport_preference}': sport_preference_data}, w)

        return user_to_delete
    else:
        raise HTTPException(status_code=404, detail=f"User {username} not found")


def create_sport_preference(username: str, password: str, sport_name: str):
    user_data = load_json(json_filename_user)
    sport_data = load_json(json_filename_sport)
    sport_preference_data = load_json(json_filename_sport_preference)

    sport_name = sport_name.lower()

    sport_id = next((sport['SportID'] for sport in sport_data if sport['SportName'].lower() == sport_name), None)
    if sport_id is None:
        raise HTTPException(status_code=404, detail=f"Sport {sport_name} not found")

    user = next((user for user in user_data if user['UserName'] == username), None)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User {username} not found")

    if user['Password'] != password:
        raise HTTPException(status_code=400, detail=f"Wrong password")

    if any(pref for pref in sport_preference_data if pref['UserID'] == user['UserID'] and pref['SportID'] == sport_id):
        raise HTTPException(status_code=400, detail=f"User {username} already has sport preference {sport_name}")

    new_sport_preference = {
        "UserID": user['UserID'],
        "SportID": sport_id
    }
    sport_preference_data.append(new_sport_preference)

    with open(f'{json_folder}/{json_filename_sport_preference}.json', 'w') as f:
        json.dump({f'{json_filename_sport_preference}': sport_preference_data}, f)

    return new_sport_preference

def delete_sport_preference(username: str, password: str, sport_name: str):
    user_data = load_json(json_filename_user)
    sport_data = load_json(json_filename_sport)
    sport_preference_data = load_json(json_filename_sport_preference)

    sport_name = sport_name.lower()

    sport_id = next((sport['SportID'] for sport in sport_data if sport['SportName'].lower() == sport_name), None)
    if sport_id is None:
        raise HTTPException(status_code=404, detail=f"Sport {sport_name} not found")

    user = next((user for user in user_data if user['UserName'] == username), None)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User {username} not found")

    if user['Password'] != password:
        raise HTTPException(status_code=400, detail=f"Wrong password")

    sport_preference = next((pref for pref in sport_preference_data if pref['UserID'] == user['UserID'] and pref['SportID'] == sport_id), None)
    if sport_preference is None:
        raise HTTPException(status_code=400, detail=f"User {username} does not have sport preference {sport_name}")

    sport_preference_data.remove(sport_preference)

    with open(f'{json_folder}/{json_filename_sport_preference}.json', 'w') as f:
        json.dump({f'{json_filename_sport_preference}': sport_preference_data}, f)

    return sport_preference

