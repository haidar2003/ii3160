from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordRequestForm
from models import *
from user import *
from matchup import *
from sport import *
from rollcall_integration import *
from datetime import timedelta


app = FastAPI()

# Index
@app.get("/")
def index():
    return {"details": "Halo :D, kalau mau akses tolong ketik /docs ya ^w^"}


# Login
@app.post("/token", response_model=Token)
async def get_token(form_data: OAuth2PasswordRequestForm = Depends()):
    return generate_token(form_data.username, form_data.password)


# Register
@app.post("/register", response_model=User)
async def register_user(user: UserCreate):
    return create_user(user)


# Mencari profil pengguna lain berdasarkan kota pengguna
@app.get('/matchup/user/city', response_model=List[UserItemResponse])
async def get_user_by_city_matchup(current_user: User = Depends(get_current_active_user)):
    return read_user_by_city_matchup(current_user.UserName)


# Mencari profil pengguna lain berdasarkan preferensi olahraga pengguna
@app.get('/matchup/user/sport', response_model=List[UserItemResponse])
async def get_users_by_sport_matchup(current_user: User = Depends(get_current_active_user)):
    return read_user_by_sport_matchup(current_user.UserName)


# Mencari profil orang lain berdasarkan preferensi olahraga dan kota pengguna
@app.get('/matchup/user', response_model=List[UserItemResponse])
async def get_users_by_city_and_sport_matchup(current_user: User = Depends(get_current_active_user)):
    return read_user_by_city_and_sport_matchup(current_user.UserName)


# Mencari venue olahraga berdasarkan kota pengguna
@app.get('/matchup/venue', response_model=List[VenueItemResponse])
async def get_venues_by_city_matchup(current_user: User = Depends(get_current_active_user)):
    return read_venues_by_city_matchup(current_user.UserName)


# Mencari event olahraga berdasarkan kota pengguna
@app.get('/matchup/event/', response_model=List[EventItemResponse])
async def get_events_by_user_city(current_user: User = Depends(get_current_active_user)):
    return read_events_by_city_matchup(current_user.UserName)


# Membuat booking venue olahraga baru
@app.post('/matchup/{venue_id}/booking')
async def add_booking(venue_id: int, event_date: DateItem, current_user: User = Depends(get_current_active_user)):
    return create_booking(current_user.UserName, venue_id, event_date)


# Membuat event olahraga baru
@app.post('/matchup/event/')
async def add_event(event_details: EventItem, current_user: User = Depends(get_current_active_user)):
    return create_event(current_user.UserName, event_details)


# Menampilkan profil sendiri
@app.get("/user/me/profile", response_model=UserItemResponse)
async def read_user_me(current_user: User = Depends(get_current_active_user)):
    return read_my_profile(current_user.UserName)


# Membaca semua profil orang dengan password yang telah di-hash
@app.get('/user/search/all/password')
async def read_all_user_with_password(current_user: User = Depends(get_current_active_user)):
    with open("data/user.json","r") as f:
        user = json.load(f)

    return user['user']


# Menampilkan semua profil pengguna
@app.get('/user/search/all', response_model=List[UserItemResponse])
async def get_all_user(current_user: User = Depends(get_current_active_user)):
    return read_all_user()


# Menampilkan profil pengguna dengan username tertentu
@app.get('/user/search/username/{username}', response_model=UserItemResponse)
async def get_user_by_username(username: str, current_user: User = Depends(get_current_active_user)):
    return read_user_by_username(username)


# Menampilkan profil pengguna berdasarkan preferensi olahraga tertentu
@app.get('/user/search/sport/{sport_name}', response_model=List[UserItemResponse])
async def get_user_by_sport(sport_name: str, current_user: User = Depends(get_current_active_user)):
    return read_user_by_sport(sport_name)


# Menampilkan profil pengguna di kota tertentu
@app.get('/user/search/city/{city_name}', response_model=List[UserItemResponse])
async def get_user_by_city_name(city_name: str, current_user: User = Depends(get_current_active_user)):
    return read_user_by_city(city_name)


# Memperbarui profil pengguna
@app.put('/user/me/profile')
async def update_user_details(updated_user: UserItemUpdate, current_user: User = Depends(get_current_active_user)):
    return update_user(current_user.UserName, updated_user)


# Memperbarui password pengguna
@app.put('/user/me/password')
async def change_password(new_password: str, current_user: User = Depends(get_current_active_user)):
    return update_user_password(current_user.UserName, new_password)


# Menghapus profil pengguna
@app.delete('/user/me/delete', response_model=dict)
async def remove_user(current_user: User = Depends(get_current_active_user)):
    deleted_user = delete_user(current_user.UserName)

    expires_delta = timedelta(seconds=3)
    new_token = create_access_token(data={"sub": current_user.UserName}, expires_delta=expires_delta)

    return deleted_user


# Menambahkan preferensi olahraga ke profil pengguna
@app.post('/user/me/sport')
async def add_user_sport_preference(sport_name: str, current_user: User = Depends(get_current_active_user)):
    return create_sport_preference(current_user.UserName, sport_name)


# Menghapus preferensi olahraga dari profil pengguna
@app.delete('/user/me/sport')
async def remove_user_sport_preference(sport_name: str, current_user: User = Depends(get_current_active_user)):
    return delete_sport_preference(current_user.UserName, sport_name)


# Menampilkan semua olahraga di aplikasi
@app.get('/sport', response_model=List[SportItem])
async def get_all_sports(current_user: User = Depends(get_current_active_user)):
    return read_all_sport()


# Menambahkan olahraga ke aplikasi
@app.post('/sport', response_model=SportItem)
async def add_sport(sport_name: str, current_user: User = Depends(get_current_active_user)):
    return create_sport(sport_name)


# Menghapus olahraga dari aplikasi
@app.delete('/sport', response_model=SportItem)
async def remove_sport(sport_name: str, current_user: User = Depends(get_current_active_user)):
    return delete_sport(sport_name)


# Menampilkan semua venue olahraga di aplikasi
@app.get('/venue', response_model=List[VenueItemResponse])
async def get_all_venue(current_user: User = Depends(get_current_active_user)):
    return read_all_venue()


# Menampilkan semua event olahraga di aplikasi
@app.get('/event', response_model=List[EventItemResponse])
async def get_all_event(current_user: User = Depends(get_current_active_user)):
    return read_all_event()


# Berpartisipasi dalam event olahraga pengguna lain
@app.post('/event/{event_id}/join/')
async def add_event_participation(event_id: int, current_user: User = Depends(get_current_active_user)):
    return create_event_participation(current_user.UserName, event_id)


# Integrasi dengan Roll Call, menambah preferensi boardgame
@app.post('/user/boardgame')
async def add_user_boardgame(boardgame_id: int, current_user: User = Depends(get_current_active_user)):
    return add_boardgame(current_user.UserName, boardgame_id)

# Integrasi dengan Roll Call, menghapus preferensi boardgame
@app.delete('/user/boardgame')
async def remove_user_boardgame(boardgame_id: int, current_user: User = Depends(get_current_active_user)):
    return remove_boardgame(current_user.UserName, boardgame_id)

# Integrasi dengan Roll Call, mencari profil pengguna dengan preferensi boardgame yang sama
@app.get('/matchup/rollcall/matchmaking')
async def matchmaking(current_user: User = Depends(get_current_active_user)):
    return matchmaking_rollcall(current_user.UserName)