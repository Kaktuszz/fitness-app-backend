from enum import Enum

class GenderEnum(str, Enum):
    male = "Male"
    female = "Female"

class ExperienceLevelEnum(str, Enum):
    beginner = "Beginner"
    intermediate = "Intermediate"
    advanced = "Advanced"