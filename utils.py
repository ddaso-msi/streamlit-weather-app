from datetime import datetime, timedelta

def round_datetime(start_datetime):
    """
    Round the given datetime to the nearest hour by setting minutes and seconds to 0.
    If the minutes are 30 or more, round up to the next hour.
    """
    # Calculate the number of minutes past the hour
    minutes = start_datetime.minute

    # Round to the nearest hour
    if minutes >= 30:
        # Set minutes and seconds to 0 and add 1 hour
        rounded_start_datetime = start_datetime.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    else:
        # Set minutes and seconds to 0
        rounded_start_datetime = start_datetime.replace(minute=0, second=0, microsecond=0)

    return rounded_start_datetime