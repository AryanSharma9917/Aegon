import sys
from difflib import SequenceMatcher
from typing import NoReturn, Union

from pyicloud import PyiCloudService
from pyicloud.exceptions import (PyiCloudAPIResponseException,
                                 PyiCloudFailedLoginException)
from pyicloud.services.findmyiphone import AppleDevice

from executors.location import get_location_from_coordinates
from executors.word_match import word_match
from modules.audio import listener, speaker
from modules.conditions import keywords
from modules.exceptions import EgressErrors
from modules.logger.custom_logger import logger
from modules.models import models
from modules.utils import shared, support


def device_selector(phrase: str) -> Union[AppleDevice, None]:
    """Selects a device using the received input string.

    Args:
        phrase: Takes the voice recognized statement as argument.

    Returns:
        AppleDevice:
        Returns the selected device from the class ``AppleDevice``
    """
    icloud_api = PyiCloudService(models.env.icloud_user, models.env.icloud_pass)
    devices = [device for device in icloud_api.devices]
    devices_str = [{str(device).split(":")[0].strip(): str(device).split(":")[1].strip()} for device in devices]
    closest_match = [
        (SequenceMatcher(a=phrase, b=key).ratio() + SequenceMatcher(a=phrase, b=val).ratio()) / 2
        for device in devices_str for key, val in device.items()
    ]
    index = closest_match.index(max(closest_match))
    return icloud_api.devices[index]


def location_services(device: AppleDevice) -> Union[None, dict]:
    """Gets the current location of an Apple device.

    Args:
        device: Particular Apple device that has to be located.

    Returns:
        dict:
        Dictionary of location information.
    """
    try:
        if raw_location := device.location():
            return get_location_from_coordinates(coordinates=(raw_location["latitude"], raw_location["longitude"]))
        else:
            logger.error(f"Unable to retrieve location for the device: {device!r}")
            return
    except PyiCloudAPIResponseException as error:
        logger.error(f"Unable to retrieve location for the device: {device!r}")
        logger.error(error)
        return


def locate_device(target_device: AppleDevice) -> NoReturn:
    """Speaks the location information of the target device.

    Args:
        target_device: Takes the target device as an argument.
    """
    try:
        location = location_services(device=target_device)
    except EgressErrors as error:
        logger.error(error)
        speaker.speak(text="I was unable to connect to the internet. Please check your connection settings and retry.",
                      run=True)
        return
    lookup = str(target_device).split(":")[0].strip()
    if not location:
        speaker.speak(text=f"I wasn't able to locate your {lookup} {models.env.title}! It is probably offline.")
    else:
        if shared.called_by_offline:
            post_code = location.get("postcode", "").split("-")[0]
        else:
            post_code = '"'.join(list(location.get("postcode", "").split("-")[0]))
        iphone_location = f"Your {lookup} is near {location.get('road')}, " \
                          f"{location.get('city', location.get('residential'))} " \
                          f"{location.get('state')}. Zipcode: {post_code}, {location.get('country')}"
        stat = target_device.status()
        bat_percent = f"Battery: {round(stat['batteryLevel'] * 100)} %, " if stat["batteryLevel"] else ""
        device_model = stat["deviceDisplayName"]
        phone_name = stat["name"]
        speaker.speak(text=f"{iphone_location}. Some more details. {bat_percent} Name: {phone_name}, "
                           f"Model: {device_model}")


def locate(phrase: str) -> None:
    """Locates an Apple device using icloud api for python.

    Args:
        phrase: Takes the voice recognized statement as argument and extracts device name from it.
    """
    if not all([models.env.icloud_user, models.env.icloud_pass]):
        logger.warning("ICloud username or password not found.")
        support.no_env_vars()
        return
    try:
        target_device = device_selector(phrase=phrase)
    except PyiCloudFailedLoginException as error:
        logger.error(error)
        speaker.speak(text=f"I ran into an authentication error {models.env.title}! "
                           "Please check the logs for more information.")
        return
    except PyiCloudAPIResponseException as error:
        logger.error(error)
        speaker.speak(text=f"I was unable to get the device information {models.env.title}!"
                           "Please check the logs for more information.")
        return
    if shared.called_by_offline:
        locate_device(target_device=target_device)
        return
    sys.stdout.write(f"\rLocating your {target_device}")
    target_device.play_sound()
    before_keyword, keyword, after_keyword = str(target_device).partition(":")  # partitions the hostname info
    if before_keyword == "Accessory":
        after_keyword = after_keyword.replace(f"{models.env.name}’s", "").replace(f"{models.env.name}'s", "").strip()
        speaker.speak(text=f"I've located your {after_keyword} {models.env.title}!")
    else:
        speaker.speak(text=f"Your {before_keyword} should be ringing now {models.env.title}!")
    speaker.speak(text="Would you like to get the location details?", run=True)
    if not (phrase_location := listener.listen()):
        return
    elif word_match(phrase=phrase_location, match_list=keywords.keywords.ok):
        return

    locate_device(target_device=target_device)
    if models.env.icloud_recovery:
        speaker.speak(text="I can also enable lost mode. Would you like to do it?", run=True)
        phrase_lost = listener.listen()
        if word_match(phrase=phrase_lost, match_list=keywords.keywords.ok):
            target_device.lost_device(number=models.env.icloud_recovery, text="Return my phone immediately.")
            speaker.speak(text="I've enabled lost mode on your phone.")
        else:
            speaker.speak(text=f"No action taken {models.env.title}!")
