from pydantic import BaseModel
from typing import List

class DateItem(BaseModel):
    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: int

class EventItem(BaseModel):
    event_name: str
    event_date: DateItem
    description: str
    province: str
    city: str
    street: str

class EventItemResponse(BaseModel):
    EventID: int
    EventName: str
    EventOrganizer: str
    EventDate: str
    Description: str
    Province: str
    City: str
    Street: str

class SportItem(BaseModel):
    SportID: int
    SportName: str

class VenueItemResponse(BaseModel):
    VenueID: int
    VenueName: str
    VenueManager: str
    Price: int
    Province: str
    City: str
    Street: str
    Description: str

class UserItem(BaseModel):
    UserName: str or None = None
    UserEmail: str or None = None
    Password: str or None = None
    Description: str or None = None
    Province: str or None = None
    City: str or None = None
    Street: str or None = None
    DisplayName: str or None = None
    
class UserItemUpdate(BaseModel):
    UserEmail: str
    Description: str
    Province: str
    City: str
    Street: str
    DisplayName: str

class UserItemResponse(BaseModel):
    UserName: str
    UserEmail: str
    Description: str
    Province: str
    City: str
    Street: str
    DisplayName: str
    Sports: List[str]

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    Username: str or None = None

class UserBase(BaseModel):
    UserName: str or None = None
    UserEmail: str or None = None
    Description: str or None = None
    Province: str or None = None
    City: str or None = None
    Street: str or None = None
    DisplayName: str or None = None

class User(UserBase):
    Disabled: bool or None = None

class UserInDB(User):
    HashedPassword: str

class UserCreate(UserBase):
    Password: str