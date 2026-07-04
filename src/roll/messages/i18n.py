from roll.messages.doctor import RU as DOCTOR_RU
from roll.messages.normalize import RU as NORMALIZE_RU
from roll.messages.cli import Msg


RU = {**{value.key: value.ru for value in Msg.__dict__.values() if hasattr(value, "key")}, **DOCTOR_RU, **NORMALIZE_RU}


def text(key: str, **kwargs) -> str:
    value = getattr(Msg, key.split(".", 1)[1].upper(), None) if key.startswith("cli.") else None
    if value is not None:
        resolved = str(value)
    else:
        resolved = DOCTOR_RU.get(key) or NORMALIZE_RU.get(key) or key
    return resolved.format(**kwargs) if kwargs else resolved
