from enum import IntEnum


class ChooseStatus(IntEnum):
    NOT_CHOOSING = 0
    CHOOSING_FIRST_BLOCK = 1
    CHOOSING_SECOND_BLOCK = 2
