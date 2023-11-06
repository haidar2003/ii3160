from fastapi import FastAPI, HTTPException
from models import *
from user import *
from matchup import *
from sport import *

app = FastAPI()

@app.get("/")
def index():
    return {"details": "Halo :D, kalau mau akses tolong ketik /docs ya ^w^"}

@app.get('/matchup/user/city', response_model=List[UserItemResponse])
async def get_user_by_city_matchup(username: str, password: str):
    return read_user_by_city_matchup(username, password)

@app.get('/matchup/user/sport', response_model=List[UserItemResponse])
async def get_users_by_sport_matchup(username: str, password: str):
    return read_user_by_sport_matchup(username, password)

@app.get('/matchup/user', response_model=List[UserItemResponse])
async def get_users_by_city_and_sport_matchup(username: str, password: str):
    return read_user_by_city_and_sport_matchup(username, password)

@app.get('/matchup/venue', response_model=List[VenueItemResponse])
async def get_venues_by_city_matchup(username: str, password: str):
    return read_venues_by_city_matchup(username, password)

@app.get('/matchup/event/', response_model=List[EventItemResponse])
async def get_events_by_user_city(username: str, password: str):
    return read_events_by_city_matchup(username, password)

@app.post('/matchup/booking/{venue_id}')
async def add_booking(username: str, password: str, venue_id: int, event_date: DateItem):
    return create_booking(username, password, venue_id, event_date)
    
@app.post('/matchup/event/{username}')
async def add_event(username: str, password: str, event_details: EventItem):
    return create_event(username, password, event_details)

@app.get('/user', response_model=List[UserItemResponse])
async def get_all_user():
    return read_all_user()

@app.get('/user/password')
async def read_all_user_with_password():
    with open("data/user.json","r") as f:
        user = json.load(f)

    return user['user']

@app.get('/user/search/username/{username}', response_model=UserItemResponse)
async def get_user_by_username(username: str):
    return read_user_by_username(username)

@app.get('/user/search/sport/{sport_name}', response_model=List[UserItemResponse])
async def get_user_by_sport(sport_name: str):
    return read_user_by_sport(sport_name)

@app.get('/user/search/city/{city_name}', response_model=List[UserItemResponse])
async def get_user_by_city_name(city_name: str):
    return read_user_by_city(city_name)

@app.post('/user')
async def add_user(user_details: UserItem):
    return create_user(user_details)

@app.put('/user/{username}')
async def update_user_details(username: str, password: str, updated_user: UserItemUpdate):
    return update_user(username, password, updated_user)
    
@app.post('/user/{username}/sport/{sport_name}')
async def add_user_sport_preference(username: str, password: str, sport_name: str):
    return create_sport_preference(username, password, sport_name)

@app.delete('/user/{username}/sport/{sport_name}')
async def remove_user_sport_preference(username: str, password: str, sport_name: str):
    return delete_sport_preference(username, password, sport_name)

@app.delete('/user/{username}')
async def remove_user(username: str, password: str):
    return delete_user(username, password)
        
@app.get('/sport', response_model=List[SportItem])
async def get_all_sports():
    return read_all_sport()

@app.post('/sport/{sport_name}', response_model=SportItem)
async def add_sport(sport_name: str):
    return create_sport(sport_name)

@app.delete('/sport/{sport_name}', response_model=SportItem)
async def remove_sport(sport_name: str):
    return delete_sport(sport_name)

@app.get('/venue', response_model=List[VenueItemResponse])
async def get_all_venue():
    return read_all_venue()

@app.get('/event', response_model=List[EventItemResponse])
async def get_all_event():
    return read_all_event()

@app.post('/event/{event_id}/join/{username}')
async def add_event_participation(username: str, password: str, event_id: int):
    return create_event_participation(username, password, event_id)