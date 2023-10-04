# appdaemon-schedule
A simple scheduler for Home Assistant/AppDaemon.
Originally written for controlling an irrigation system, but can be used to control anything with a binary on/off function.

## Install
- Download this repository, and copy the "schedule" folder to "appdaemon/apps".
- Add your configuration to `apps.yaml` using one of the examples below.


## Example `apps.yaml` configuration
```yaml
# Irrigation system
my_schedules:
  module: schedule
  class: Schedule
  schedules:
    water_the_plants:
      on_at: "8:00:00" # All times are 24hr
      off_at: "8:10:00"
      target_entity: switch.irrigator_switch
```


<b>TODO:</b>
- Add the ability to specify run conditions for schedules
- Allow for specifying a run duration instead of an end time
