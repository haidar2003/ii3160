from pydantic import BaseModel
from typing import List

class UserItem(BaseModel):
    UserName: str
    UserEmail: str
    Password: str
    Description: str
    Province: str
    City: str
    Street: str
    DisplayName: str
    
class UserItemUpdate(BaseModel):
    UserEmail: str
    Password: str
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

class SportItem(BaseModel):
    SportID: int
    SportName: str

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


class VenueItemResponse(BaseModel):
    VenueID: int
    VenueName: str
    VenueManager: str
    Price: int
    Province: str
    City: str
    Street: str
    Description: str