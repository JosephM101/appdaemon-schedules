# Schedule
# Written by Joseph Mignone
# 10/4/2023
# Version 1.0.1

import appdaemon.plugins.hass.hassapi as hass
from datetime import datetime
from datetime import time

# Variable considerations:
#
# react_immediately_when_condition_changes: Bool
#   If the condition changes, react immediately. For example, if the condition evaluates to 'True', and we're within the time that the entity should be on, turn the entity on immediately instead of waiting for the next cycle. Defaults to False.

class Schedule(hass.Hass):
    def initialize(self):
        self.schedules = self.args.get("schedules", {})
        # self.log(self.schedules)
        for schedule_name, schedule_info in self.schedules.items():
            on_time = self.parse_time(self.convert_time(schedule_info["on_at"]))
            off_time = self.parse_time(self.convert_time(schedule_info["off_at"]))

            target_entity = schedule_info["target_entity"]

            now = datetime.now().time()
            self.log(now)
            if time_is_within_range(now, on_time, off_time):
                self.turn_on({"entity": target_entity})
            else:
                self.turn_off({"entity": target_entity})
            
            self.run_daily(self.turn_on, on_time, entity=target_entity)
            self.run_daily(self.turn_off, off_time, entity=target_entity)
            self.log(f"Established schedule \"{schedule_name}\" (on at {on_time}, off at {off_time})")

    def turn_on(self, kwargs):
        entity = kwargs["entity"]
        self.log(f"Turning {entity} on")
        self.call_service("homeassistant/turn_on", entity_id=entity)

    def turn_off(self, kwargs):
        entity = kwargs["entity"]
        self.log(f"Turning {entity} off")
        self.call_service("homeassistant/turn_off", entity_id=entity)

    def convert_time(self, on_time):
        error_message_function_name = "convert_time"
        acceptable_value_error_message = "Acceptable values are AM and PM."
        parameter_must_be_defined_error_message = lambda x : f"parameter '{x}' must be defined!"

        if isinstance(on_time, str):
            return on_time  # Assume that it is already in 24-hour format
        else: # Convert 12hr to 24hr
            hour = on_time.get('hour')
            minute = on_time.get('minute', 0) # These can be default to 0
            second = on_time.get('second', 0) # These can be default to 0
            meridiem = on_time.get('meridiem')

            if hour is None:
                raise ValueError(f"{error_message_function_name}: {parameter_must_be_defined_error_message('hour')}")

            if meridiem is None:
                raise ValueError(f"{error_message_function_name}: {parameter_must_be_defined_error_message('meridiem')} {acceptable_value_error_message}")

            if meridiem.lower() == 'pm':
                # convert
                if hour != 12:
                    hour += 12
            elif meridiem.lower() == 'am':
                # convert
                if hour == 12:
                    hour = 0
            else:
                raise ValueError(f"{error_message_function_name}: 'meridiem': bad value. {acceptable_value_error_message} Got '{meridiem}'")

            return f"{hour:02d}:{minute:02d}:{second:02d}"


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
