# This lets us distinguish between a validation error and other (unwanted) errors
class ValidationException(Exception):
    pass


class MissingDataException(Exception):
    pass
