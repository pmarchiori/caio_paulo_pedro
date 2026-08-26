from models import Event
from typing import Optional
 
api_list: list[Event] = []
 
 
def add_event(event: Event) -> Event:
    api_list.append(event)
    return event
 
 
def get_all_events() -> list[Event]:
    return api_list
 
 
def get_event_by_id(event_id: int) -> Optional[Event]:
    for event in api_list:
        if event.id == event_id:
            return event
    return None