from enum import Enum


class BaseEnum(str, Enum):
    def __str__(self):
        return str(self.value)

    @classmethod
    def get_list(cls):
        return [getattr(cls, attr) for attr in dir(cls) if attr.isupper()]


class EvaluationMode(BaseEnum):
    STANDARD = "standard"
    ASSESSMENT = "assessment"


class SettingKey(BaseEnum):
    pass
