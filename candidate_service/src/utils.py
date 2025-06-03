import re


def is_valid_uuid4(s: str) -> bool:

    regex = re.compile(
        r"^[a-f0-9]{8}-"
        r"[a-f0-9]{4}-"
        r"4[a-f0-9]{3}-"
        r"[89ab][a-f0-9]{3}-"
        r"[a-f0-9]{12}\Z",
        re.I,
    )
    return bool(regex.match(s))
