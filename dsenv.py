"""
Damn Simple Environ Vars
(c) 2026 Marcin Nowak / marcin.j.nowak@gmail.com
"""

import io
import os


def parse_envfile(buffer: io.TextIOBase) -> dict:
    data = {}

    for raw_line in buffer.read().split("\n"):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("export "):
            line = line.split("export")[1].strip()

        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            continue
        value = value.strip()

        if value.startswith(("'", '"')):
            quote = value[0]
            if value.endswith(quote):
                value = value[1:-1]
            else:
                end = value.find(quote, 1)
                if end != -1:
                    value = value[1:end]
        else:
            if "#" in value:
                value = value.split("#", 1)[0].rstrip()
        data[key] = value
    return data


def load_env(path: str = "~/.env", override: bool = False) -> None:
    full_path = os.path.expanduser(path)
    with open(full_path, "r") as buf:
        data = parse_envfile(buf)
        for key, value in data.items():
            if key not in os.environ or override:
                os.environ[key] = value
