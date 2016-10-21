

class RoutineException(Exception):

    def __init__(self, error_code, message=None, aditional_exception=None):
        self.error_code = error_code
        if not message and aditional_exception:
            self.message = str(aditional_exception)
        else:
            self.message = message