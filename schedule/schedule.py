# Schedule
# Written by Joseph Mignone
# 10/4/2023

import appdaemon.plugins.hass.hassapi as hass
from datetime import datetime
from datetime import time

class Schedule(hass.Hass):
    def initialize(self):
        self.schedules = self.args.get("schedules", {})
        for schedule_name, schedule_info in self.schedules.items():
            on_time = self.parse_time(schedule_info["on_at"])
            off_time = self.parse_time(schedule_info["off_at"])
            target_entity = schedule_info["target_entity"]

            # Based on the time right now, decide if we should turn the entity on or off
            now = datetime.now().time()
            if time_is_within_range(now, on_time, off_time):
                self.turn_on({"entity": target_entity})
            else:
                self.turn_off({"entity": target_entity})
            
            # Set up the actual schedule part
            self.run_daily(self.turn_on, on_time, entity=target_entity)
            self.run_daily(self.turn_off, off_time, entity=target_entity)

            # Log our success
            self.log(f"Established schedule \"{schedule_name}\" (on at {on_time}, off at {off_time})")

    def turn_on(self, kwargs):
        entity = kwargs["entity"]
        self.log(f"Turning {entity} on")
        self.call_service("homeassistant/turn_on", entity_id=entity)

    def turn_off(self, kwargs):
        entity = kwargs["entity"]
        self.log(f"Turning {entity} off")
        self.call_service("homeassistant/turn_off", entity_id=entity)


def time_is_within_range(time: time, start: time, end: time) -> bool:
    """
    Check if a time is within a given range.

    Parameters:
    time (datetime.time): The time to check.
    start (datetime.time): The start of the time range.
    end (datetime.time): The end of the time range.

    Returns:
    bool: True if the time is within the range, False otherwise.
    """
    # Check if the current time is within the range
    if start <= end:
        return start <= time <= end
    else:  # Over midnight
        return start <= time or time <= end
