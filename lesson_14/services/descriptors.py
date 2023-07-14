import logging

LOGGER = logging.getLogger('server')


class Port:
    def __set__(self, instance, value):
        if not 1023 < value < 65536:
            LOGGER.critical(
                f"Try to run server with invalid port {value}. "
                f"Valid values 1024 - 65535.")
            exit(1)
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name
