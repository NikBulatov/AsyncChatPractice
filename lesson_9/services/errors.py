class IncorrectDataReceivedError(Exception):
    """Incorrect data received from the socket"""

    def __str__(self):
        return "An incorrect message was received from a remote computer."


class ServerError(Exception):
    """Server error"""

    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text


class NonDictionaryInputError(Exception):
    """The function argument is not a dictionary"""

    def __str__(self):
        return "The function argument must be a dictionary."


class RequiredFieldMissingError(Exception):
    """A required field is missing in the accepted dictionary"""

    def __init__(self, missing_field):
        self.missing_field = missing_field

    def __str__(self):
        return (f"There is no required field "
                f"in the accepted dictionary {self.missing_field}.")
