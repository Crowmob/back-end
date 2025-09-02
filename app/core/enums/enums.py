from enum import Enum


class RoleEnum(Enum):
    MEMBER = "MEMBER"
    ADMIN = "ADMIN"
    OWNER = "OWNER"


class FileFormat(Enum):
    CSV = "csv"
    JSON = "json"
