"""
    Bevim Protocol
"""


# This flag is used to inform the control system to start the experiment
START_EXPERIMENT_FLAG = bytes([1])

# This flag is used to inform the control system to stop the experiment
STOP_EXPERIMENT_FLAG = bytes([1])

# This flag is used to ask to the control system the list of the present sensors
GET_AVAILABLE_SENSORS_FLAG = bytes([2])

TIMESTAMP_HEADER = 1

TIMESTAMP_BYTES_QUANTITY = 3

SENSOR_BYTES_QUANTITY = 2

FREQUENCY_FLAG_HEADER = 3

SENSOR_LSB_RESOLUTION = 16384

def get_sensor_data_pattern():
    SENSOR_DATA_PATTERN_REGEX = r'^([A-Za-z\d]+),([-]?\d*[\.]?\d+)?,([-]?\d*[\.]?\d+)?,([-]?\d*[\.]?\d+)?,([-]?\d*[\.]?\d+)?\r\n$'
    import re
    sensor_data_pattern_regex = re.compile(SENSOR_DATA_PATTERN_REGEX)
    return sensor_data_pattern_regex


MAX_SENSORS = 16

def validate_sensor_number_and_axis(sensor_number, axis):
    valid = (axis >= 1 and axis <= 3) and (sensor_number >= 1 and sensor_number <= MAX_SENSORS)
    return valid
