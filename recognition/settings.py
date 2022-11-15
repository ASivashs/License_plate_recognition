import sys


def check_slash():
    return "/" if sys.platform == "Linux" else "\\"
    