from datetime import datetime
import uuid
import os


def get_file_name(f: str, s: dict):
    options = {
        "ltime": datetime.now().strftime('%Y-%m-%d-%H-%M-%S'),
        "stime": datetime.now().strftime('%Y-%m-%d'),
        "uuid": uuid.uuid4(),
        **s
    }

    filename = f.format(**options)

    return os.path.realpath(f"./output/{filename}.pdf")
