import contextlib
import os


# From https://stackoverflow.com/a/24469659/2605678
@contextlib.contextmanager
def cd(path):
    old_path = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_path)
