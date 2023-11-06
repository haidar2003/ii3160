import json
from typing import List

from fastapi import HTTPException
from models import *
from datetime import *

json_folder = "data"
json_filename_user = "user"
json_filename_sport = "sport"
json_filename_sport_preference = "sport_preference"
json_filename_venue = "venue"
json_filename_booking = "booking"
json_filename_event = "event"
json_filename_event_participant = "event_participant"
json_filename_venue_manager = "venue_manager"

def load_json(filename):
    with open(f"{json_folder}/{filename}.json","r") as f:
        data = json.load(f)[filename]
    return data

def read_user_by_sport(sport_name: str) -> List[UserItemResponse]:
    user_data = load_json(json_filename_user)
    sport_data = load_json(json_filename_sport)
    sport_preference_data = load_json(json_filename_sport_preference)

    sport_names = {sport['SportID']: sport['SportName'] for sport in sport_data}

    sport_name = sport_name.lower()

    sport_id = next((sport['SportID'] for sport in sport_data if sport['SportName'].lower() == sport_name), None)
    if sport_id is None:
        raise HTTPException(status_code=404, detail=f"Sport {sport_name} does not exists")

    user_id_list = [pref['UserID'] for pref in sport_preference_data if pref['SportID'] == sport_id]

    valid_user_list = []
    for user in user_data:
        if user['UserID'] in user_id_list:
            user_sports = [sport_names[pref['SportID']] for pref in sport_preference_data if pref['UserID'] == user['UserID']]
            temp = UserItemResponse(**{k: v for k, v in user.items() if k != 'Password'}, Sports=user_sports)
            valid_user_list.append(temp)

    return valid_user_list


def read_user_by_city(city_name: str) -> List[UserItemResponse]:
    user_data = load_json(json_filename_user)
    sport_data = load_json(json_filename_sport)
    sport_preference_data = load_json(json_filename_sport_preference)

    sport_names = {sport['SportID']: sport['SportName'] for sport in sport_data}

    city_name = city_name.lower()

    valid_user_list = []
    for user in user_data:
        if user['City'].lower() == city_name:
            user_sports = [sport_names[pref['SportID']] for pref in sport_preference_data if pref['UserID'] == user['UserID']]
            temp = UserItemResponse(**{k: v for k, v in user.items() if k != 'Password'}, Sports=user_sports)
            valid_user_list.append(temp)

    return valid_user_list

def create_booking(username: str, password: str, venue_id: int, event_date: DateItem):
    user_data = load_json(json_filename_user)
    venues_data = load_json(json_filename_venue)
    bookings_data = load_json(json_filename_booking)

    user = next((user for user in user_data if user['UserName'] == username), None)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User {username} not found")

    if user['Password'] != password:
        raise HTTPException(status_code=400, detail=f"Wrong password")

    venue = next((venue for venue in venues_data if venue['VenueID'] == venue_id), None)
    if not venue:
        raise HTTPException(status_code=404, detail="Venue ID does not exists")

    if not validate_event_date(event_date):
        raise HTTPException(status_code=400, detail="Date is invalid")

    event_date_fixed = format_event_date(event_date)
    existing_booking = next((booking for booking in bookings_data if booking['VenueID'] == venue_id and booking['UserID'] == user['UserID'] and booking['BookingDate'] == event_date_fixed), None)
    if existing_booking:
        raise HTTPException(status_code=400, detail="Booking already exists")

    booking_id = len(bookings_data) + 1

    transaction_id = len(bookings_data) + 1

    new_booking = {
        "BookingID": booking_id,
        "VenueID": venue_id,
        "UserID": user['UserID'],
        "BookingDate": event_date_fixed,
        "TransactionID": transaction_id
    }

    bookings_data.append(new_booking)

    with open(f"{json_folder}/{json_filename_booking}.json", "w") as f:
        json.dump({json_filename_booking: bookings_data}, f, indent=4)

    return new_booking

def create_event(username: str, password: str, event_details: EventItem):
    user_data = load_json(json_filename_user)
    event_data = load_json(json_filename_event)
    event_participant_data = load_json(json_filename_event_participant)

    user = next((user for user in user_data if user['UserName'] == username), None)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User {username} not found")

    if user['Password'] != password:
        raise HTTPException(status_code=400, detail=f"Wrong password")

    if not validate_event_date(event_details.event_date):
        raise HTTPException(status_code=400, detail="Date is invalid")

    event_date_fixed = format_event_date(event_details.event_date)
    existing_event = next((event for event in event_data if event['EventName'] == event_details.event_name and event['EventOrganizer'] == user['UserID'] and event['EventDate'] == event_date_fixed and event['Description'] == event_details.description and event['Province'] == event_details.province and event['City'] == event_details.city and event['Street'] == event_details.street), None)
    if existing_event:
        raise HTTPException(status_code=400, detail="Event already exists")

    event_id = len(event_data) + 1

    new_event = {
        "EventID": event_id,
        "EventName": event_details.event_name,
        "EventOrganizer": user['UserID'],
        "EventDate": event_date_fixed,
        "Description": event_details.description,
        "Province": event_details.province,
        "City": event_details.city,
        "Street": event_details.street
    }

    event_data.append(new_event)

    with open(f"{json_folder}/{json_filename_event}.json", "w") as f:
        json.dump({json_filename_event: event_data}, f, indent=4)

    new_participant = {
        "EventID": event_id,
        "UserID": user['UserID']
    }
    event_participant_data.append(new_participant)

    with open(f"{json_folder}/{json_filename_event_participant}.json", "w") as f:
        json.dump({json_filename_event_participant: event_participant_data}, f, indent=4)

    return new_event

def read_all_venue() -> List[VenueItemResponse]:
    venue_data = load_json(json_filename_venue)
    venue_manager_data = load_json(json_filename_venue_manager)

    manager_name = {manager['ManagerID']: manager['DisplayName'] for manager in venue_manager_data}

    return [VenueItemResponse(**{**venue, 'VenueManager': manager_name.get(venue.pop('VenueManager'), 'Unknown')}) for venue in venue_data]

def read_venues_by_city_matchup(username: str, password: str) -> List[VenueItemResponse]:
    user_data = load_json(json_filename_user)
    venue_data = load_json(json_filename_venue)
    venue_manager_data = load_json(json_filename_venue_manager)

    manager_name = {manager['ManagerID']: manager['DisplayName'] for manager in venue_manager_data}

    user = next((user for user in user_data if user['UserName'] == username), None)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User {username} not found")

    if user['Password'] != password:
        raise HTTPException(status_code=400, detail=f"Wrong password")

    city_name = user['City'].lower()

    valid_venue_list = []
    for venue in venue_data:
        if venue['City'].lower() == city_name:
            venue['VenueManager'] = manager_name.get(venue['VenueManager'], 'Unknown')  # Get the manager's name
            valid_venue_list.append(VenueItemResponse(**venue))

    return valid_venue_list

def read_all_event() -> List[EventItemResponse]:
    event_data = load_json(json_filename_event)
    user_data = load_json(json_filename_user)

    user_name = {user['UserID']: user['DisplayName'] for user in user_data}

    return [EventItemResponse(**{**event, 'EventOrganizer': user_name.get(event.pop('EventOrganizer'), 'Unknown')}) for event in event_data]

def read_events_by_city_matchup(username: str, password: str) -> List[EventItemResponse]:
    user_data = load_json(json_filename_user)
    event_data = load_json(json_filename_event)

    user = next((user for user in user_data if user['UserName'] == username), None)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User {username} not found")

    if user['Password'] != password:
        raise HTTPException(status_code=400, detail=f"Wrong password")

    city_name = user['City'].lower()

    user_name = {user['UserID']: user['DisplayName'] for user in user_data}

    valid_event_list = []
    for event in event_data:
        if event['City'].lower() == city_name:
            valid_event_list.append(EventItemResponse(**{**event, 'EventOrganizer': user_name.get(event.pop('EventOrganizer'), 'Unknown')}))

    return valid_event_list

def create_event_participation(username: str, password: str, event_id: int):
    user_data = load_json(json_filename_user)
    event_data = load_json(json_filename_event)
    event_participant_data = load_json(json_filename_event_participant)

    user = next((user for user in user_data if user['UserName'] == username), None)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User {username} not found")

    if user['Password'] != password:
        raise HTTPException(status_code=400, detail=f"Wrong password")

    if any(part for part in event_participant_data if part['UserID'] == user['UserID'] and part['EventID'] == event_id):
        raise HTTPException(status_code=400, detail=f"User {username} participation already exists")

    event = next((event for event in event_data if event['EventID'] == event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail=f"Event ID {event_id} not found")
    
    new_participant = {
        "EventID": event_id,
        "UserID": user['UserID']
    }
    event_participant_data.append(new_participant)

    with open(f"{json_folder}/{json_filename_event_participant}.json", "w") as f:
        json.dump({json_filename_event_participant: event_participant_data}, f)

    return new_participant

def read_user_by_city_matchup(username: str, password: str) -> List[UserItemResponse]:
    user_data = load_json(json_filename_user)
    sport_data = load_json(json_filename_sport)
    sport_preference_data = load_json(json_filename_sport_preference)

    sport_names = {sport['SportID']: sport['SportName'] for sport in sport_data}

    user = next((user for user in user_data if user['UserName'] == username), None)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User {username} not found")

    if user['Password'] != password:
        raise HTTPException(status_code=400, detail=f"Wrong password")

    city_name = user['City'].lower()

    valid_user_list = []
    for user in user_data:
        if user['UserName'] == username: 
            continue
        if user['City'].lower() == city_name:
            user_sports = [sport_names[pref['SportID']] for pref in sport_preference_data if pref['UserID'] == user['UserID']]
            temp = UserItemResponse(**{k: v for k, v in user.items() if k != 'Password'}, Sports=user_sports)
            valid_user_list.append(temp)

    return valid_user_list

def read_user_by_sport_matchup(username: str, password: str) -> List[UserItemResponse]:
    user_data = load_json(json_filename_user)
    sport_data = load_json(json_filename_sport)
    sport_preference_data = load_json(json_filename_sport_preference)

    sport_names = {sport['SportID']: sport['SportName'] for sport in sport_data}

    user = next((user for user in user_data if user['UserName'] == username), None)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User {username} not found")

    if user['Password'] != password:
        raise HTTPException(status_code=400, detail=f"Wrong password")

    user_sport_ids = [pref['SportID'] for pref in sport_preference_data if pref['UserID'] == user['UserID']]

    valid_user_list = []
    for user in user_data:
        if user['UserName'] == username: 
            continue
        user_sports = [sport_names[pref['SportID']] for pref in sport_preference_data if pref['UserID'] == user['UserID']]
        if any(sport_id in user_sport_ids for sport_id in [pref['SportID'] for pref in sport_preference_data if pref['UserID'] == user['UserID']]):
            temp = UserItemResponse(**{k: v for k, v in user.items() if k != 'Password'}, Sports=user_sports)
            valid_user_list.append(temp)

    return valid_user_list

def read_user_by_city_and_sport_matchup(username: str, password: str) -> List[UserItemResponse]:
    user_data = load_json(json_filename_user)
    sport_data = load_json(json_filename_sport)
    sport_preference_data = load_json(json_filename_sport_preference)

    sport_names = {sport['SportID']: sport['SportName'] for sport in sport_data}

    user = next((user for user in user_data if user['UserName'] == username), None)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User {username} not found")

    if user['Password'] != password:
        raise HTTPException(status_code=400, detail=f"Wrong password")

    city_name = user['City'].lower()
    user_sport_ids = [pref['SportID'] for pref in sport_preference_data if pref['UserID'] == user['UserID']]

    valid_user_list = []
    for user in user_data:
        if user['UserName'] == username: 
            continue
        if user['City'].lower() == city_name:
            user_sports = [sport_names[pref['SportID']] for pref in sport_preference_data if pref['UserID'] == user['UserID']]
            if any(sport_id in user_sport_ids for sport_id in [pref['SportID'] for pref in sport_preference_data if pref['UserID'] == user['UserID']]):
                temp = UserItemResponse(**{k: v for k, v in user.items() if k != 'Password'}, Sports=user_sports)
                valid_user_list.append(temp)

    return valid_user_list

def validate_event_date(event_date: DateItem):
    if event_date.year < 1 or event_date.month < 1 or event_date.month > 12 or event_date.day < 1:
        return False

    month_details = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    if event_date.day > month_details[event_date.month - 1]:
        return False

    if event_date.hour < 0 or event_date.hour > 23 or event_date.minute < 0 or event_date.minute > 59 or event_date.second < 0 or event_date.second > 59:
        return False

    return True

def format_event_date(event_date: DateItem):
    return f"{event_date.year:04d}-{event_date.month:02d}-{event_date.day:02d} {event_date.hour:02d}:{event_date.minute:02d}:{event_date.second:02d}"