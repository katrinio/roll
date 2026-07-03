from roll.messages.cli import RU as CLI_RU
from roll.messages.doctor import RU as DOCTOR_RU
from roll.messages.normalize import RU as NORMALIZE_RU


RU = {**CLI_RU, **DOCTOR_RU, **NORMALIZE_RU}


def text(key: str, **kwargs) -> str:
    value = RU[key]
    return value.format(**kwargs) if kwargs else value

