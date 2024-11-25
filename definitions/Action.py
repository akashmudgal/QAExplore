from enum import Enum

class Action(Enum):
    LEFT_CLICK = 1      # Left click Action
    RIGHT_CLICK = 2     # Right Click action
    DBL_CLICK = 3       # Double click action
    HOVER = 4           # Hover over element action
    HANDLE_SELECT = 5   # Handle Selet tag action
    TYPE_TEXT = 6       # Type text action