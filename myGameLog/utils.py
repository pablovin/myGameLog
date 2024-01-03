import os


def remove_last_empty_row(csv_directory):
    with open(csv_directory, "r+") as f:
        f.seek(0, 2)
        size = f.tell()
        f.truncate(size - 1)
