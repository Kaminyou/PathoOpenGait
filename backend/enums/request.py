import enum


class Status(enum.Enum):
    INQUEUE = 1
    COMPUTING = 2
    DONE = 3
    ERROR = 4
