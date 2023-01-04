# noinspection PyUnresolvedReferences
"""This is a space for support functions used across different modules.

>>> Support

"""

import hashlib
import math
import os
import random
import re
import socket
import string
import sys
import time
import uuid
from datetime import datetime, timezone
from difflib import SequenceMatcher
from typing import Any, Hashable, List, NoReturn, Union

import dateutil.tz
import inflect
import psutil
import yaml
from holidays import country_holidays

from executors.internet import ip_address
from modules.audio import speaker
from modules.conditions import keywords
from modules.database import database
from modules.logger.custom_logger import logger
from modules.models import models

db = database.Database(database=models.fileio.base_db)


def hostname_to_ip(hostname: str, localhost: bool = True) -> List[str]:
    """Uses ``socket.gethostbyname_ex`` to translate a host name to IPv4 address format, extended interface.

    See Also:
        - A host may have multiple interfaces.
        - | In case of true DNS being used or the host entry file is carefully handwritten, the system will look
          | there to find the translation.
        - | But depending on the configuration, the host name can be bound to all the available interfaces, including
          | the loopback ones.
        - ``gethostbyname`` returns the address of the first of those interfaces in its own order.
        - | To get the assigned IP, ``gethostbyname_ex`` is used, which returns a list of all the interfaces, including
          | the host spot connected, and loopback IPs.

    References:
        https://docs.python.org/3/library/socket.html#socket.gethostbyname_ex

    Args:
        hostname: Takes the hostname of a device as an argument.
        localhost: Takes a boolean value to behave differently in case of localhost.
    """
    try:
        _hostname, _alias_list, _ipaddr_list = socket.gethostbyname_ex(hostname)
    except socket.error as error:
        logger.error(f"{error} on {hostname}")
        return []
    logger.debug({"Hostname": _hostname, "Alias": _alias_list, "Interfaces": _ipaddr_list})
    if not _ipaddr_list:
        logger.critical(f"No interfaces found for {hostname}")
    elif len(_ipaddr_list) > 1:
        logger.warning(f"Host {hostname} has multiple interfaces. {_ipaddr_list}") if localhost else None
        return _ipaddr_list
    else:
        if localhost:
            ip_addr = ip_address()
            if _ipaddr_list[0].split('.')[0] == ip_addr.split('.')[0]:
                return _ipaddr_list
            else:
                logger.error(f"NetworkID of the InterfaceIP of host {hostname!r} does not match the network id of the "
                             f"DeviceIP.")
                return []
        else:
            return _ipaddr_list


def celebrate() -> str:
    """Function to look if the current date is a holiday or a birthday.

    Returns:
        str:
        A string of the event observed today.
    """
    day = datetime.today().date()
    us_holidays = country_holidays("US").get(day)  # checks if the current date is a US holiday
    in_holidays = country_holidays("IND", prov="TN", state="TN").get(day)  # checks if Indian (esp TN) holiday
    if in_holidays:
        return in_holidays
    elif us_holidays and "Observed" not in us_holidays:
        return us_holidays
    elif models.env.birthday == datetime.now().strftime("%d-%B"):
        return "Birthday"


def part_of_day() -> str:
    """Checks the current hour to determine the part of day.

    Returns:
        str:
        Morning, Afternoon, Evening or Night based on time of day.
    """
    current_hour = int(datetime.now().strftime("%H"))
    if 5 <= current_hour <= 11:
        return "Morning"
    if 12 <= current_hour <= 15:
        return "Afternoon"
    if 16 <= current_hour <= 19:
        return "Evening"
    return "Night"


def time_converter(seconds: float) -> str:
    """Modifies seconds to appropriate days/hours/minutes/seconds.

    Args:
        seconds: Takes number of seconds as argument.

    Returns:
        str:
        Seconds converted to days or hours or minutes or seconds.
    """
    days = round(seconds // 86400)
    seconds = round(seconds % (24 * 3600))
    hours = round(seconds // 3600)
    seconds %= 3600
    minutes = round(seconds // 60)
    seconds %= 60
    if days and hours and minutes and seconds:
        return f"{days} days, {hours} hours, {minutes} minutes, and {seconds} seconds"
    elif days and hours and minutes:
        return f"{days} days, {hours} hours, and {minutes} minutes"
    elif days and hours:
        return f"{days} days, and {hours} hours"
    elif days:
        return f"{days} days"
    elif hours and minutes and seconds:
        return f"{hours} hours, {minutes} minutes, and {seconds} seconds"
    elif hours and minutes:
        return f"{hours} hours, and {minutes} minutes"
    elif hours:
        return f"{hours} hours"
    elif minutes and seconds:
        return f"{minutes} minutes, and {seconds} seconds"
    elif minutes:
        return f"{minutes} minutes"
    else:
        return f"{seconds} seconds"


def get_capitalized(phrase: str, dot: bool = True) -> Union[str, None]:
    """Looks for words starting with an upper-case letter.

    Args:
        phrase: Takes input string as an argument.
        dot: Takes a boolean flag whether to include words separated by (.) dot.

    Returns:
        str:
        Returns the upper case words if skimmed.
    """
    place = ""
    for word in phrase.split():
        if word[0].isupper() and word.lower() not in keywords.keywords.avoid:
            place += word + " "
        elif "." in word and dot:
            place += word + " "
    return place.strip() if place.strip() else None


def get_closest_match(text: str, match_list: list) -> str:
    """Get the closest matching word from a list of words.

    Args:
        text: Text to look for in the matching list.
        match_list: List to be compared against.

    Returns:
        str:
        Returns the text that matches closest in the list.
    """
    closest_match = [{"key": key, "val": SequenceMatcher(a=text, b=key).ratio()} for key in match_list]
    return sorted(closest_match, key=lambda d: d["val"], reverse=True)[0].get("key")


def unrecognized_dumper(train_data: dict) -> NoReturn:
    """If none of the conditions are met, converted text is written to a yaml file for training purpose.

    Args:
        train_data: Takes the dictionary that has to be written as an argument.
    """
    dt_string = datetime.now().strftime("%B %d, %Y %H:%M:%S.%f")[:-3]
    data = {}
    if os.path.isfile(models.fileio.training_data):
        try:
            with open(models.fileio.training_data) as reader:
                data = yaml.load(stream=reader, Loader=yaml.FullLoader) or {}
        except yaml.YAMLError as error:
            logger.error(error)
            os.rename(
                src=models.fileio.training_data,
                dst=str(models.fileio.training_data).replace(".", f"_{datetime.now().strftime('%m_%d_%Y_%H_%M')}.")
            )
        for key, value in train_data.items():
            if data.get(key):
                data[key].update({dt_string: value})
            else:
                data.update({key: {dt_string: value}})

    if not data:
        data = {key1: {dt_string: value1} for key1, value1 in train_data.items()}

    data = {
        func: {
            dt: unrec for dt, unrec in sorted(unrec_dict.items(), reverse=True,
                                              key=lambda item: datetime.strptime(item[0], "%B %d, %Y %H:%M:%S.%f"))
        } for func, unrec_dict in data.items()
    }

    with open(models.fileio.training_data, 'w') as writer:
        yaml.dump(data=data, stream=writer, sort_keys=False)


def size_converter(byte_size: int) -> str:
    """Gets the current memory consumed and converts it to human friendly format.

    Args:
        byte_size: Receives byte size as argument.

    Returns:
        str:
        Converted understandable size.
    """
    if not byte_size:
        byte_size = psutil.Process(pid=models.settings.pid).memory_info().rss
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    index = int(math.floor(math.log(byte_size, 1024)))
    return f"{round(byte_size / pow(1024, index), 2)} {size_name[index]}"


def comma_separator(list_: list) -> str:
    """Separates commas using simple ``.join()`` function and analysis based on length of the list taken as argument.

    Args:
        list_: Takes a list of elements as an argument.

    Returns:
        str:
        Comma separated list of elements.
    """
    return ", and ".join([", ".join(list_[:-1]), list_[-1]] if len(list_) > 2 else list_)


def extract_time(input_: str) -> List[str]:
    """Extracts 12-hour time value from a string.

    Args:
        input_: Int if found, else returns the received float value.

    Returns:
        list:
        Extracted time from the string.
    """
    return re.findall(r'(\d+:\d+\s?(?:a.m.|p.m.:?))', input_) or \
        re.findall(r'(\d+\s?(?:a.m.|p.m.:?))', input_) or \
        re.findall(r'(\d+:\d+\s?(?:am|pm:?))', input_) or \
        re.findall(r'(\d+\s?(?:am|pm:?))', input_)


def extract_nos(input_: str, method: type = float) -> Union[int, float]:
    """Extracts number part from a string.

    Args:
        input_: Takes string as an argument.
        method: Takes a type to return a float or int value.

    Returns:
        float:
        Float values.
    """
    if value := re.findall(r"\d+", input_):
        if method == float:
            try:
                return method(".".join(value))
            except ValueError as error:
                caller = sys._getframe(1).f_code.co_name  # noqa
                logger.error(error)
                logger.error(f"Called by: {caller!r}")
                method = int
        if method == int:
            return method("".join(value))


def format_nos(input_: float) -> int:
    """Removes ``.0`` float values.

    Args:
        input_: Strings or integers with ``.0`` at the end.

    Returns:
        int:
        Int if found, else returns the received float value.
    """
    return int(input_) if isinstance(input_, float) and input_.is_integer() else input_


def extract_str(input_: str) -> str:
    """Extracts strings from the received input.

    Args:
        input_: Takes a string as argument.

    Returns:
        str:
        A string after removing special characters.
    """
    return "".join([i for i in input_ if not i.isdigit() and i not in [",", ".", "?", "-", ";", "!", ":"]]).strip()


def matrix_to_flat_list(input_: List[list]) -> List:
    """Converts a matrix into flat list.

    Args:
        input_: Takes a list of list as an argument.

    Returns:
        list:
        Flat list.
    """
    return sum(input_, []) or [item for sublist in input_ for item in sublist]


def remove_duplicates(input_: List[Any]) -> List[Any]:
    """Remove duplicate values from a list.

    Args:
        input_: Takes a list as an argument.

    Returns:
        list:
        Returns a cleaned up list.
    """
    # return list(set(input_))
    return [i.strip() for n, i in enumerate(input_) if i not in input_[n + 1:]]


def words_to_number(input_: str) -> int:
    """Converts words into integers.

    Args:
        input_: Takes an integer wording as an argument.

    Returns:
        int:
        Integer version of the words.
    """
    input_ = input_.lower()
    number_mapping = {
        'zero': 0,
        'one': 1,
        'two': 2,
        'three': 3,
        'four': 4,
        'five': 5,
        'six': 6,
        'seven': 7,
        'eight': 8,
        'nine': 9,
        'ten': 10,
        'eleven': 11,
        'twelve': 12,
        'thirteen': 13,
        'fourteen': 14,
        'fifteen': 15,
        'sixteen': 16,
        'seventeen': 17,
        'eighteen': 18,
        'nineteen': 19,
        'twenty': 20,
        'thirty': 30,
        'forty': 40,
        'fifty': 50,
        'sixty': 60,
        'seventy': 70,
        'eighty': 80,
        'ninety': 90,
    }
    numbers = []
    for word in input_.replace('-', ' ').split():
        if word in number_mapping:
            numbers.append(number_mapping[word])
        elif word == 'hundred':
            numbers[-1] *= 100
        elif word == 'thousand':
            numbers = [x * 1000 for x in numbers]
        elif word == 'million':
            numbers = [x * 1000000 for x in numbers]
    return sum(numbers)


def number_to_words(input_: Union[int, str], capitalize: bool = False) -> str:
    """Converts integer version of a number into words.

    Args:
        input_: Takes the integer version of a number as an argument.
        capitalize: Boolean flag to capitalize the first letter.

    Returns:
        str:
        String version of the number.
    """
    result = inflect.engine().number_to_words(num=input_)
    return result[0].upper() + result[1:] if capitalize else result


def lock_files(alarm_files: bool = False, reminder_files: bool = False) -> List[str]:
    """Checks for ``*.lock`` files within the ``alarm`` directory if present.

    Args:
        alarm_files: Takes a boolean value to gather list of alarm lock files.
        reminder_files: Takes a boolean value to gather list of reminder lock files.

    Returns:
        list:
        List of ``*.lock`` file names ignoring other hidden files.
    """
    if alarm_files:
        return [f for f in os.listdir("alarm") if not f.startswith(".")] if os.path.isdir("alarm") else None
    if reminder_files:
        return [f for f in os.listdir("reminder") if not f.startswith(".")] if os.path.isdir("reminder") else None


def check_restart() -> List[str]:
    """Checks for entries in the restart table in base db.

    Returns:
        list:
        Returns the flag, caller from the restart table.
    """
    with db.connection:
        cursor = db.connection.cursor()
        flag = cursor.execute("SELECT flag, caller FROM restart").fetchone()
        cursor.execute("DELETE FROM restart")
        db.connection.commit()
    return flag


def convert_utc_to_local(utc_dt: datetime) -> datetime:
    """Converts UTC datetime object to local datetime object.

    Args:
        utc_dt: Takes UTC datetime object as an argument

    Returns:
        datetime:
        Local datetime as an object.
    """
    utc_dt = utc_dt.replace(tzinfo=timezone.utc)  # Tell datetime object that the tz is UTC
    local_tz = dateutil.tz.gettz(datetime.now().astimezone().tzname())  # Get local timezone
    return utc_dt.astimezone(local_tz)  # Convert the UTC timestamp to local


def check_stop() -> List[str]:
    """Checks for entries in the stopper table in base db.

    Returns:
        list:
        Returns the flag, caller from the stopper table.
    """
    with db.connection:
        cursor = db.connection.cursor()
        flag = cursor.execute("SELECT flag, caller FROM stopper").fetchone()
        cursor.execute("DELETE FROM stopper")
        db.connection.commit()
    return flag


def exit_message() -> str:
    """Variety of exit messages based on day of week and time of day.

    Returns:
        str:
        A greeting bye message.
    """
    am_pm = datetime.now().strftime("%p")  # current part of day (AM/PM)
    hour = datetime.now().strftime("%I")  # current hour
    day = datetime.now().strftime("%A")  # current day

    if am_pm == "AM" and int(hour) < 10:
        exit_msg = f"Have a nice day, and happy {day}."
    elif am_pm == "AM" and int(hour) >= 10:
        exit_msg = f"Enjoy your {day}."
    elif am_pm == "PM" and (int(hour) == 12 or int(hour) < 3) and day in ["Friday", "Saturday"]:
        exit_msg = "Have a nice afternoon, and enjoy your weekend."
    elif am_pm == "PM" and (int(hour) == 12 or int(hour) < 3):
        exit_msg = "Have a nice afternoon."
    elif am_pm == "PM" and int(hour) < 6 and day in ["Friday", "Saturday"]:
        exit_msg = "Have a nice evening, and enjoy your weekend."
    elif am_pm == "PM" and int(hour) < 6:
        exit_msg = "Have a nice evening."
    elif day in ["Friday", "Saturday"]:
        exit_msg = "Have a nice night, and enjoy your weekend."
    else:
        exit_msg = "Have a nice night."

    if event := celebrate():
        exit_msg += f"\nAnd by the way, happy {event}"

    return exit_msg


def no_env_vars() -> NoReturn:
    """Says a message about permissions when env vars are missing."""
    logger.error(f"Called by: {sys._getframe(1).f_code.co_name}")  # noqa
    speaker.speak(text=f"I'm sorry {models.env.title}! I lack the permissions!")


def flush_screen() -> NoReturn:
    """Flushes the screen output."""
    if models.settings.ide:
        sys.stdout.flush()
        sys.stdout.write("\r")
    else:
        sys.stdout.flush()
        sys.stdout.write(f"\r{' '.join(['' for _ in range(os.get_terminal_size().columns)])}")


def block_print() -> NoReturn:
    """Suppresses print statement."""
    sys.stdout = open(os.devnull, 'w')


def release_print() -> NoReturn:
    """Removes print statement's suppression."""
    sys.stdout = sys.__stdout__


def remove_file(filepath: str, delay: int = 0) -> NoReturn:
    """Deletes the requested file after a certain time.

    Args:
        filepath: Filepath that has to be removed.
        delay: Delay in seconds after which the requested file is to be deleted.
    """
    time.sleep(delay)
    os.remove(filepath) if os.path.isfile(filepath) else logger.error(f"{filepath} not found.")


def stop_process(pid: int) -> NoReturn:
    """Stop a particular process using ``SIGTERM`` and ``SIGKILL`` signals.

    Args:
        pid: Process ID that has to be shut down.
    """
    try:
        proc = psutil.Process(pid=pid)
        if proc.is_running():
            proc.terminate()
        time.sleep(0.5)
        if proc.is_running():
            proc.kill()
    except psutil.NoSuchProcess as error:
        logger.error(error)


def hashed(key: uuid.UUID) -> Hashable:
    """Generates sha from UUID.

    Args:
        key: Takes the UUID generated as an argument.

    Returns:
        str:
        Hashed value of the UUID received.
    """
    return hashlib.sha1(key.bytes + bytes(key.hex, "utf-8")).digest().hex()


def token() -> Hashable:
    """Generates a token using hashed uuid4.

    Returns:
        str:
        Returns hashed UUID as a string.
    """
    return hashed(key=uuid.uuid4())


def keygen_str(length: int, punctuation: bool = False) -> str:
    """Generates random key.

    Args:
        length: Length of the keygen.
        punctuation: A boolean flag to include punctuation in the keygen.

    Returns:
        str:
        Random key of specified length.
    """
    if punctuation:
        required_str = string.ascii_letters + string.digits + string.punctuation
    else:
        required_str = string.ascii_letters + string.digits
    return "".join(random.choices(required_str, k=length))


def keygen_uuid(length: int = 32) -> str:
    """Generates random key from hex-d UUID.

    Args:
        length: Length of the required key.

    Returns:
        str:
        Random key of specified length.
    """
    return uuid.uuid4().hex.upper()[0:length]
