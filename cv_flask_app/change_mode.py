from datetime import datetime


def get_time():
    t = datetime.now().hour
    if 6 < t < 18:
        return 'light'
    else:
        return 'dark'
    