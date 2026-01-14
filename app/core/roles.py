# app/core/roles.py
from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"
