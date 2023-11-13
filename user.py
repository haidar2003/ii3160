import json
from typing import List
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from models import *
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = "856ee52ce0026cf03bb3835bc5c4ef3c84016d457a52f2a7d9f26212c4c9bd99"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

json_folder = "data"
json_filename_user = "user"
json_filename_sport = "sport"
json_filename_sport_preference = "sport_preference"

def load_json(filename):
    with open(f"{json_folder}/{filename}.json","r") as f:
        data = json.load(f)[filename]
    return data


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Fungsi-fungsi untuk otentikasi
# Mengecek apakah password sesuai
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Membuat password yang telah di-hash
def get_password_hash(password):
    return pwd_context.hash(password)

# Mengambil informasi pengguna dari basis data
def get_user(username: str):
    user_data = load_json(json_filename_user)
    for user in user_data:
        if user['UserName'] == username:
            return UserInDB(**user)

# Melakukan otentikasi pengguna  
def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.HashedPassword):
        return False

    return user

# Membuat token akses
def create_access_token(data: dict, expires_delta: timedelta or None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt

# Mengambil pengguna yang sedang di laman
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user credentials", headers={"WWW-Authenticate": "Bearer"})

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception
    
        token_data = TokenData(Username=username)

    except JWTError:
        raise credential_exception

    user = get_user(username=token_data.Username)
    if user is None:
        raise credential_exception
    
    return user

# Mengambil pengguna yang sedang menggunakan laman
async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if current_user.Disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return current_user


# Fungsi-fungsi utama
# Mengotentikasi pengguna dan memberikan pengguna tersebut token akses (Login)
def generate_token(username: str, password: str):
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.UserName}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


# Mendaftarkan pengguna baru (Register)
def create_user(user_details: UserCreate):
    user_data = load_json(json_filename_user)

    existing_usernames = set(item['UserName'] for item in user_data)
    if user_details.UserName in existing_usernames:
        raise HTTPException(status_code=400, detail=f"User {user_details.UserName} already exists")
    
    user_id = len(user_data)
    
    new_user = {
        "UserID": user_id,
        "UserName": user_details.UserName,
        "UserEmail": user_details.UserEmail,
        "HashedPassword": get_password_hash(user_details.Password),
        "Description": user_details.Description,
        "Province": user_details.Province,
        "City": user_details.City,
        "Street": user_details.Street,
        "DisplayName": user_details.DisplayName,
        "Disabled": False
    }

    user_data.append(new_user)

    with open(f'{json_folder}/{json_filename_user}.json', "w") as w:
            json.dump({f'{json_filename_user}': user_data}, w)
        
    return new_user


# Menampilkan profil sendiri
def read_my_profile(username: str) -> UserItemResponse:
    user_data = next((item for item in load_json(json_filename_user) if item['UserName'] == username), None)
    sport_data = load_json(json_filename_sport)
    sport_preference_data = load_json(json_filename_sport_preference)

    return UserItemResponse(**{k: v for k, v in user_data.items() if k != 'Password'}, Sports=[sport['SportName'] for sport in sport_data if any(pref['UserID'] == user_data['UserID'] and pref['SportID'] == sport['SportID'] for pref in sport_preference_data)])


# Menampilkan semua profil pengguna
def read_all_user() -> List[UserItemResponse]:
    user_data = load_json(json_filename_user)
    sport_data = load_json(json_filename_sport)
    sport_preference_data = load_json(json_filename_sport_preference)
    return [UserItemResponse(**{k: v for k, v in user.items() if k != 'Password'}, Sports=[sport['SportName'] for sport in sport_data if any(pref['UserID'] == user['UserID'] and pref['SportID'] == sport['SportID'] for pref in sport_preference_data)]) for user in user_data]


# Menampilkan profil pengguna dengan username tertentu
def read_user_by_username(username: str) -> UserItemResponse:
    user_data = next((item for item in load_json(json_filename_user) if item['UserName'] == username), None)
    sport_data = load_json(json_filename_sport)
    sport_preference_data = load_json(json_filename_sport_preference)

    if user_data is None:
        raise HTTPException(status_code=404, detail=f"User {username} not found")
    return UserItemResponse(**{k: v for k, v in user_data.items() if k != 'Password'}, Sports=[sport['SportName'] for sport in sport_data if any(pref['UserID'] == user_data['UserID'] and pref['SportID'] == sport['SportID'] for pref in sport_preference_data)])


# Memperbarui profil pengguna
def update_user(username, updated_user: UserItemUpdate):
    user_data = load_json(json_filename_user)
    user = next((item for item in user_data if item['UserName'] == username), None)

    updated_fields = updated_user.dict(exclude_unset=True)
    user.update(updated_fields)
    with open(f'{json_folder}/{json_filename_user}.json', "w") as w:
        json.dump({f'{json_filename_user}': user_data}, w)
    return user
    

# Memperbarui password pengguna
def update_user_password(username: str, new_password: str):
    user_data = load_json(json_filename_user)
    user = next((item for item in user_data if item['UserName'] == username), None)
    
    new_hashed_password = get_password_hash(new_password)

    user['HashedPassword'] = new_hashed_password

    with open(f'{json_folder}/{json_filename_user}.json', "w") as w:
        json.dump({f'{json_filename_user}': user_data}, w)

    return user


# Menghapus profil pengguna
def delete_user(username):
    user_data = load_json(json_filename_user)
    sport_preference_data = load_json(json_filename_sport_preference)

    user_to_delete = next((item for item in user_data if item['UserName'] == username), None)
    
    user_data = [user for user in user_data if user['UserName'] != username]
    with open(f'{json_folder}/{json_filename_user}.json', "w") as w:
        json.dump({f'{json_filename_user}': user_data}, w)

    sport_preference_data = [pref for pref in sport_preference_data if pref['UserID'] != user_to_delete['UserID']]
    with open(f'{json_folder}/{json_filename_sport_preference}.json', "w") as w:
        json.dump({f'{json_filename_sport_preference}': sport_preference_data}, w)

    return user_to_delete


# Menambahkan preferensi olahraga ke profil pengguna
def create_sport_preference(username: str, sport_name: str):
    user_data = load_json(json_filename_user)
    sport_data = load_json(json_filename_sport)
    sport_preference_data = load_json(json_filename_sport_preference)

    sport_name = sport_name.lower()

    sport_id = next((sport['SportID'] for sport in sport_data if sport['SportName'].lower() == sport_name), None)
    if sport_id is None:
        raise HTTPException(status_code=404, detail=f"Sport {sport_name} not found")

    user = next((user for user in user_data if user['UserName'] == username), None)

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


# Menghapus preferensi olahraga dari profil pengguna
def delete_sport_preference(username: str, sport_name: str):
    user_data = load_json(json_filename_user)
    sport_data = load_json(json_filename_sport)
    sport_preference_data = load_json(json_filename_sport_preference)

    sport_name = sport_name.lower()

    sport_id = next((sport['SportID'] for sport in sport_data if sport['SportName'].lower() == sport_name), None)
    if sport_id is None:
        raise HTTPException(status_code=404, detail=f"Sport {sport_name} not found")

    user = next((user for user in user_data if user['UserName'] == username), None)

    sport_preference = next((pref for pref in sport_preference_data if pref['UserID'] == user['UserID'] and pref['SportID'] == sport_id), None)
    if sport_preference is None:
        raise HTTPException(status_code=400, detail=f"User {username} does not have sport preference {sport_name}")

    sport_preference_data.remove(sport_preference)

    with open(f'{json_folder}/{json_filename_sport_preference}.json', 'w') as f:
        json.dump({f'{json_filename_sport_preference}': sport_preference_data}, f)

    return sport_preference





