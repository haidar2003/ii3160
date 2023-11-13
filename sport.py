import json

from fastapi import HTTPException
from models import *
from typing import List

json_folder = "data"
json_filename = f"{json_folder}/sport.json"

with open(json_filename,"r") as read_file:
    data = json.load(read_file)


# Menampilkan semua olahraga di aplikasi
def read_all_sport() -> List[SportItem]:
    return [SportItem(**sport) for sport in data['sport']]


# Menambahkan olahraga ke aplikasi
def create_sport(sport_name: str) -> SportItem:
    existing_sport_names = set(sport['SportName'].lower() for sport in data['sport'])
    if sport_name.lower() in existing_sport_names:
        raise HTTPException(status_code=400, detail=f"Sport {sport_name} already exists")
    
    existing_id = set(sport['SportID'] for sport in data['sport'])
    new_id = 1
    while new_id in existing_id:
        new_id += 1
    
    new_sport = {
        "SportID": new_id,
        "SportName": sport_name.lower()
    }

    data['sport'].append(new_sport)

    with open(json_filename, "w") as write_file:
        json.dump(data, write_file)
        
    return SportItem(**new_sport)


# Menghapus olahraga dari aplikasi
def delete_sport(sport_name: str) -> SportItem:
    existing_sport = next((sport for sport in data['sport'] if sport['SportName'].lower() == sport_name.lower()), None)
    
    if existing_sport:
        data['sport'] = [sport for sport in data['sport'] if sport['SportName'].lower() != sport_name.lower()]
        with open(json_filename, "w") as write_file:
            json.dump(data, write_file)
        return SportItem(**existing_sport)
    else:
        raise HTTPException(status_code=404, detail=f"Sport {sport_name} not found")
