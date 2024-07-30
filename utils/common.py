import re
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed


def thread(rows, function):
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_row = {executor.submit(
            function, index, row): row for index, row in enumerate(rows)}

        for future in as_completed(future_to_row):
            try:
                future.result()
            except Exception as e:
                print(e)


def to_text(text):
    if (isinstance(text, int) or (isinstance(text, float)) and text.is_integer()):
        return str(int(text))

    if text:
        text = re.sub(r'[^\x20-\x7E]+', '', str(text))
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    else:
        return ""


def to_float(value):
    if value:
        try:
            value = round(float(to_text(value)), 2)
        except:
            value = 0
    else:
        value = 0

    if value == int(value):
        return int(value)
    else:
        return value


def to_int(value):
    return int(to_float(value))


def to_date(value):
    try:
        date = datetime.strptime(
            str(value), "%m/%d/%Y").date() if value else None
        return date
    except:
        return None


def to_handle(text):
    if text:
        handle = str(text).lower().replace(" ", "-")
        handle = re.sub(r'[^a-z0-9-]', '', handle)
        handle = re.sub(r'-+', '-', handle)

        return handle.strip('-')
    else:
        return ""


def find_file(filename, search_path):
    search_directory = Path(search_path)
    for path in search_directory.rglob(filename):
        if path.is_file():
            return str(path)
    return None
