import os
import shutil
from datetime import datetime


class MarketHours:
    """Initiates MarketHours object to store the market hours for each timezone in USA.

    >>> MarketHours

    See Also:
        Class variable ``hours`` contains key-value pairs for both ``EXTENDED`` and ``REGULAR`` market hours.
    """

    hours = {
        'EXTENDED': {
            'EDT': {'OPEN': 7, 'CLOSE': 18}, 'EST': {'OPEN': 7, 'CLOSE': 18},
            'CDT': {'OPEN': 6, 'CLOSE': 17}, 'CST': {'OPEN': 6, 'CLOSE': 17},
            'MDT': {'OPEN': 5, 'CLOSE': 16}, 'MST': {'OPEN': 5, 'CLOSE': 16},
            'PDT': {'OPEN': 4, 'CLOSE': 15}, 'PST': {'OPEN': 4, 'CLOSE': 15},
            'OTHER': {'OPEN': 5, 'CLOSE': 21}  # 5 AM to 9 PM
        },
        'REGULAR': {
            'EDT': {'OPEN': 9, 'CLOSE': 16}, 'EST': {'OPEN': 9, 'CLOSE': 16},
            'CDT': {'OPEN': 8, 'CLOSE': 15}, 'CST': {'OPEN': 8, 'CLOSE': 15},
            'MDT': {'OPEN': 7, 'CLOSE': 14}, 'MST': {'OPEN': 7, 'CLOSE': 14},
            'PDT': {'OPEN': 6, 'CLOSE': 13}, 'PST': {'OPEN': 6, 'CLOSE': 13},
            'OTHER': {'OPEN': 7, 'CLOSE': 19}  # 7 AM to 7 PM
        }
    }


def rh_cron_schedule(extended: bool = False) -> str:
    """Creates a cron expression for ``report_gatherer.py``. Determines cron schedule based on current timezone.

    Args:
        extended: Uses extended hours.

    See Also:
        - extended: 1 before and after market hours.
        - default(regular): Regular market hours.

    Returns:
        str:
        A crontab expression running every 30 minutes during market hours based on the current timezone.
    """
    command = f"cd {os.getcwd()} && {shutil.which(cmd='python')} {os.path.join('api', 'report_gatherer.py')}"
    tz = datetime.utcnow().astimezone().tzname()
    if tz not in MarketHours.hours['REGULAR'] or tz not in MarketHours.hours['EXTENDED']:
        tz = 'OTHER'
    start = MarketHours.hours['EXTENDED'][tz]['OPEN'] if extended else MarketHours.hours['REGULAR'][tz]['OPEN']
    end = MarketHours.hours['EXTENDED'][tz]['CLOSE'] if extended else MarketHours.hours['REGULAR'][tz]['CLOSE']
    return f"*/30 {start}-{end} * * 1-5 {command}"


def sm_cron_schedule() -> str:
    """Creates a cron expression for ``stock_monitor``.

    Returns:
        str:
        A crontab expression running every 15 minutes.
    """
    command = f"cd {os.getcwd()} && {shutil.which(cmd='python')} {os.path.join('api', 'stock_monitor.py')}"
    return f"*/15 * * * 1-5 {command}"
