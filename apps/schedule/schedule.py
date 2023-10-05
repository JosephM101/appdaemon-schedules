# Schedule
# Written by Joseph Mignone
# 10/4/2023
# Version 1.1.0

import appdaemon.plugins.hass.hassapi as hass
from datetime import datetime
from datetime import time

class Conditions:
    def __init__(self, hass, conditions, callback, schedule_entity):
        self.hass = hass
        self.conditions = conditions
        self.enabled = (conditions is not None and len(conditions) > 0)
        self.callback = callback
        self.schedule_entity = schedule_entity

        if self.enabled:
            # Establish state listeners for each sensor
            for condition in self.conditions:
                sensor = condition["sensor"]
                self.hass.listen_state(self.sensor_state_changed_callback, sensor)

    def check(self):
        if self.enabled == True:
            for condition in self.conditions:
                sensor = condition["sensor"]
                state = condition["state"]
                if self.hass.get_state(sensor) != state:
                    return False  # Something didn't pass the sniff test...
            return True  # All checks pass!
        else:
            return True  # The checks are disabled, or we don't have any conditions to meet. Give the A-OK.

    def sensor_state_changed_callback(self, entity, attribute, old, new, kwargs):
        self.schedule_entity.print_log(f"Sensor state changed for entity '{entity}': attribute '{attribute}' value changed from {old} changed to {new}")
        self.schedule_entity.print_log("Running condition check...")
        check_result = self.check()
        if check_result:
            self.schedule_entity.print_log("Conditions checked out okay")
        else:
            self.schedule_entity.print_log("Condition check failed")
        self.callback(check_result)


class ScheduleEntity():
    def __init__(self, hass, schedule_name, schedule_info):
        self.hass = hass
        self.schedule_name = schedule_name
        self.schedule_info = schedule_info

        self.on_time = self.hass.parse_time(convert_time(self.schedule_info["on_at"]))
        self.off_time = self.hass.parse_time(convert_time(self.schedule_info["off_at"]))
        self.target_entity = self.schedule_info["target_entity"]
        self.change_state_on_schedule_load = self.schedule_info.get("change_state_on_schedule_load", False)  # When the schedule is loaded, immediately determine if entity should be on or off, and set its state accordingly
        
        # Condition handling
        self.react_immediately_when_conditions_change = self.schedule_info.get("react_immediately_when_conditions_change", False)
        conditions = self.schedule_info.get("conditions", None)
        self.conditions_manager = Conditions(self.hass, conditions, self.condition_check_callback, self)

        # Create scheduled tasks
        self.hass.run_daily(self.turn_on_with_conditions, self.on_time)
        self.hass.run_daily(self.turn_off_with_conditions, self.off_time)
        self.hass.log(f"Established schedule \"{self.schedule_name}\" (on at {self.on_time}, off at {self.off_time})")

        if self.change_state_on_schedule_load:
            now = datetime.now().time()
            if time_is_within_range(now, self.on_time, self.off_time):
                self.turn_on()
            else:
                self.turn_off()


    def condition_check_callback(self, check_result):
        if check_result:
            if self.react_immediately_when_conditions_change:
                now = datetime.now().time()
                if time_is_within_range(now, self.on_time, self.off_time):
                    self.turn_on()
        else:
            if self.react_immediately_when_conditions_change:
                self.turn_off()
    
    def turn_on_with_conditions(self, kwargs):
        if self.conditions_manager.check():
            self.turn_on()
        else:
            self.print_log(f"Not turning entity \"{self.target_entity}\" on: conditions not met")

    def turn_off_with_conditions(self, kwargs):
        if self.conditions_manager.check():
            self.turn_off()
        else:
            self.print_log(f"Not turning entity \"{self.target_entity}\" off: conditions not met")

    def turn_on(self):
        self._turn_on({"entity": self.target_entity})
    
    def turn_off(self):
        self._turn_off({"entity": self.target_entity})

    # Internal functions
    def _turn_on(self, kwargs): # Pass entity to change to kwarg 'entity'
        entity = kwargs["entity"]
        self.print_log(f"Turning {entity} on")
        self.hass.call_service("homeassistant/turn_on", entity_id=entity)

    def _turn_off(self, kwargs): # Pass entity to change to kwarg 'entity'
        entity = kwargs["entity"]
        self.print_log(f"Turning {entity} off")
        self.hass.call_service("homeassistant/turn_off", entity_id=entity)

    def print_log(self, log):
        self.hass.log(f"Schedule \"{self.schedule_name}\": {log}")


class Schedule(hass.Hass):
    def initialize(self):
        self.schedules = self.args.get("schedules", {})
        self.schedule_objects = []
        
        for schedule_name, schedule_info in self.schedules.items():
            self.schedule_objects.append(ScheduleEntity(self, schedule_name, schedule_info))



def convert_time(time):
    error_message_function_name = "convert_time"
    acceptable_value_error_message = "Acceptable values are AM and PM."
    parameter_must_be_defined_error_message = lambda x : f"parameter '{x}' must be defined!"

    if isinstance(time, str):
        return time  # Assume that it is already in 24-hour format
    else: # Convert 12hr to 24hr
        hour = time.get('hour')
        minute = time.get('minute', 0) # These can be default to 0
        second = time.get('second', 0) # These can be default to 0
        meridiem = time.get('meridiem')
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
