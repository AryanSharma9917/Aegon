from enum import Enum
from logging.config import dictConfig
from typing import Dict, NoReturn, Union

import pymyq
from aiohttp import ClientSession
from pymyq.garagedoor import MyQGaragedoor

from modules.exceptions import CoverNotOnline, NoCoversFound
from modules.logger.custom_logger import logger
from modules.models import models
from modules.utils import util


class Operation(str, Enum):
    """Operations allowed on garage door.

    >>> Operation

    """

    # States of the door
    OPENING: str = "opening"
    CLOSED: str = "closed"
    CLOSING: str = "closing"

    # State of the door as well as operations to be performed
    OPEN: str = "open"
    CLOSE: str = "close"
    STATE: str = "state"


operation = Operation


async def garage_controller(execute: str, phrase: str) -> Union[Dict, NoReturn]:
    """Create an aiohttp session and run an operation on garage door.

    Args:
        phrase: Takes the recognized phrase as an argument.
        execute: Takes the operation to be performed as an argument.

    Raises:
        NoCoversFound:
        - If there were no garage doors found in the MyQ account.
        CoverNotOnline:
        - If the requested garage door is not online.

    Returns:
        dict:
        Device state information as a dictionary.
    """
    dictConfig({'version': 1, 'disable_existing_loggers': True})
    async with ClientSession() as web_session:
        myq = await pymyq.login(username=models.env.myq_username, password=models.env.myq_password,
                                websession=web_session)

        if not myq.covers:
            raise NoCoversFound("No covers found.")

        # Create a new dictionary with names as keys and MyQ object as values to get the object by name during execution
        devices: Dict[str, MyQGaragedoor] = {obj_.device_json.get('name'): obj_ for id_, obj_ in myq.covers.items()}
        logger.debug(f"Available covers: {devices}")
        device = util.get_closest_match(text=phrase, match_list=list(devices.keys()))
        logger.debug(f"Chosen cover: {device!r}")

        if not devices[device].online:
            raise CoverNotOnline(device=device, msg=f"{device!r} not online.")

        if execute == Operation.STATE:
            return devices[device].device_json

        if execute == Operation.OPEN:
            if devices[device].open_allowed:
                open_result = await devices[device].open()
                logger.debug(open_result)
                return f"Opening your {device} {models.env.title}!"
            else:
                return f"Unattended open is disabled on your {device} {models.env.title}!"
        elif execute == Operation.CLOSE:
            if devices[device].close_allowed:
                close_result = await devices[device].close()
                logger.debug(close_result)
                return f"Closing your {device} {models.env.title}!"
            else:
                return f"Unattended close is disabled on your {device} {models.env.title}!"
