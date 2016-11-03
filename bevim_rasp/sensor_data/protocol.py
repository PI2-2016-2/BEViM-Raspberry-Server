"""
    Bevim Protocol
"""


# This flag is used to inform the control system to start the experiment
START_EXPERIMENT_FLAG = '-1'

# This flag is used to inform the control system to stop the experiment
STOP_EXPERIMENT_FLAG = '-1'

# This flag is used to ask to the control system the list of the present sensors
GET_AVAILABLE_SENSORS_FLAG = '-2'

def get_sensor_data_pattern():
    SENSOR_DATA_PATTERN_REGEX = r'^([A-Za-z\d]+),([-]?\d*[\.]?\d+)?,([-]?\d*[\.]?\d+)?,([-]?\d*[\.]?\d+)?,([-]?\d*[\.]?\d+)?\r\n$'
    import re
    sensor_data_pattern_regex = re.compile(SENSOR_DATA_PATTERN_REGEX)
    return sensor_data_pattern_regex
