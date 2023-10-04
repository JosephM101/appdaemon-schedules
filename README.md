# appdaemon-schedules
A simple scheduler for Home Assistant/AppDaemon.
Originally written for controlling an irrigation system, but can be used to control anything with a binary on/off function.

I wrote this because I couldn't find a library/applet for Home Assistant that was good enough to suit my needs, so I decided to make my own, aimed at being flexible and easy to set up, even for multiple schedules.


## Install

### Install using HACS
NOTE: This applet is not currently in HACS' default repository, so it needs to be added as a custom repository.

<b>To add this repo to HACS, follow these instructions:</b>
- In your Home Assistant dashboard, click on `HACS` in the left-hand panel.
- In HACS, click `Automation`.
- At the top-left, click the three dots, and in the menu that appears, click `Custom repositories`.
- In the dialog that appears, do the following:
  - Paste this repo's URL (https://github.com/JosephM101/appdaemon-schedules) in the `Repository` box
  - Select `AppDaemon` from the `Category` drop-down menu.
  - Click `Add`
- If the repository was added successfully, you should see it in the dialog. At this point, you can close the dialog.
- Back in the `Automation` section of `HACS`, click on the `Explore & Download Repositories` button in the bottom-right corner of the page.
- In the dialog that appears, type `schedule` in the search bar, click on the result that appears, and click the `Download` button. At this point, it should be just like installing a regular HACS addon. 

### Manual install (no updates)
- Download this repository, and copy the "schedule" folder to "appdaemon/apps".
- Add your configuration to `apps.yaml` by modifying one of the examples below to fit your needs. Once you add the configuration, the module will be enabled.


## Usage

```yaml
my_schedules:
  module: schedule
  class: Schedule
  schedules: # ...
```

### Example `apps.yaml` configuration
```yaml
# Irrigation system
my_schedules:
  module: schedule
  class: Schedule
  schedules:
    water_the_plants:
      on_at: "8:00:00" # 24hr
      off_at: "8:10:00"
      target_entity: switch.irrigator_switch
```

## 12-hour (AM/PM) time support
#### <i>This feature was introduced with version 1.0.1.</i>

The variables `on_at` and `off_at`, by default, take 24-hour time strings. But optionally, you can provide 12-hour times using the `hour`, `minute`, `second` and `meridiem` parameters in place of the standard 24-hour time string.


### Here's an example of the 12-hour format in action:
```yaml
# Irrigation system
my_schedules:
  module: schedule
  class: Schedule
  schedules:
    water_the_plants:
      on_at:
        hour: 8
        meridiem: AM  # Accepts either AM or PM; not case-sensitive
      off_at: 
        hour: 8
        minute: 15
        meridiem: AM
      target_entity: switch.irrigator_switch
```
In the above example, you might have noticed that the `minute` variable was missing from `on_at`. That's because `hour` and `meridiem` are the only required variables; `minute` and `second` default to 0 if not specified.

### 12-hour time parameters:
| Parameter name | Optional | Default value | Description |
| --- | --- | --- | --- |
| `hour`     | <i> False </i> |     | An hour value (1 to 12)
| `minute`   | <i> True  </i> | `0` | A minute value (0 to 59)
| `second`   | <i> True  </i> | `0` | A second value (0 to 59)
| `meridiem` | <i> False </i> |     | AM/PM

## Condition support for schedules
#### <i>This feature was introduced with version 1.0.2.</i>
Run conditions can be used to determine if your schedule should work or not. For example, if you have an irrigation system schedule, but there's rain in the weather forecast, you can use a condition to only run the irrigation system if the forecast is sunny.

### Here's an example of the condition parameter
```yaml
# Irrigation system
my_schedules:
  module: schedule
  class: Schedule
  schedules:
    water_the_plants_on_one_condition:
      on_at: '8:00:00'
      off_at: '8:15:00'
      target_entity: switch.irrigator_switch
      conditions:
        - sensor: weather.kfmh_daynight
          state: "sunny" # Only run if it's sunny out
```


## Schedules: extra parameters
| Parameter name | Optional | Default value | Description |
| --- | --- | --- | --- |
| `[schedule].react_immediately_when_conditions_change`   | <i> True </i> | False | If set to true, as soon as a condition changes (eg. a switch is toggled), instead of waiting until the next cycle, immediately turn on/off the controlled entity (depending on whether it is supposed to be on or not)
| `[schedule].change_state_on_schedule_load`              | <i> True </i> |       | When the schedule is initialized (eg. after a settings change or at bootup), automatically set the state of the controlled entity (for example, if the current time is between the times specified in the `on_at` and `off_at` parameters, turn the entity on <i>now</i> instead of waiting for the next cycle).

## <b>TODO: Plans for the future</b>
- Allow for specifying a run duration instead of an end time
