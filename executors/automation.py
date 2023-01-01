import os
import warnings
from datetime import datetime
from string import punctuation
from typing import Union

import yaml
from deepdiff import DeepDiff

from executors.word_match import word_match
from modules.audio import speaker
from modules.logger.custom_logger import logger
from modules.models import models


def automation_handler(phrase: str) -> None:
    """Handles automation file resets by renaming it to tmp if requested to disable.

    Args:
        phrase: Takes the recognized phrase as an argument.
    """
    if "enable" in phrase:
        if os.path.isfile(models.fileio.tmp_automation):
            os.rename(src=models.fileio.tmp_automation, dst=models.fileio.automation)
            speaker.speak(text=f"Automation has been enabled {models.env.title}!")
        elif os.path.isfile(models.fileio.automation):
            speaker.speak(text=f"Automation was never disabled {models.env.title}!")
        else:
            speaker.speak(text=f"I couldn't not find the source file to enable automation {models.env.title}!")
    elif "disable" in phrase:
        if os.path.isfile(models.fileio.automation):
            os.rename(src=models.fileio.automation, dst=models.fileio.tmp_automation)
            speaker.speak(text=f"Automation has been disabled {models.env.title}!")
        elif os.path.isfile(models.fileio.tmp_automation):
            speaker.speak(text=f"Automation was never enabled {models.env.title}!")
        else:
            speaker.speak(text=f"I couldn't not find the source file to disable automation {models.env.title}!")


def rewrite_automator(write_data: dict) -> None:
    """Rewrites the automation file with the updated dictionary.

    Args:
        write_data: Takes the new dictionary as an argument.
    """
    logger.info("Data has been modified. Rewriting automation data into YAML file.")
    with open(models.fileio.automation) as file:
        try:
            read_data = yaml.load(stream=file, Loader=yaml.FullLoader) or {}
        except yaml.YAMLError as error:
            logger.error(error)
            read_data = {}
    logger.info(DeepDiff(read_data, write_data, ignore_order=True))
    with open(models.fileio.automation, 'w') as file:
        yaml.dump(data=write_data, stream=file, indent=2, sort_keys=False)


def auto_helper(offline_list: list) -> Union[str, None]:
    """Runs in a thread to help the automator function in the main module.

    Args:
        offline_list: List of offline compatible keywords.

    Returns:
        str:
        Task to be executed.
    """
    try:
        with open(models.fileio.automation) as read_file:
            automation_data = yaml.load(stream=read_file, Loader=yaml.FullLoader) or {}
    except yaml.YAMLError as error:
        logger.error(error)
        warnings.warn(
            "AUTOMATION FILE :: Invalid file format."
        )
        logger.error(f"Invalid file format. "
                     f"Logging automation data and removing the file to avoid endless errors.\n"
                     f"{''.join(['*' for _ in range(120)])}"
                     f"\n\n{read_file.read()}\n\n"
                     f"{''.join(['*' for _ in range(120)])}")
        os.remove(models.fileio.automation)
        return

    for automation_time, automation_info in automation_data.items():
        if not (exec_task := automation_info.get("task")) or \
                not word_match(phrase=exec_task, match_list=offline_list):
            logger.error("Following entry doesn't have a task or the task is not a part of offline compatible.")
            logger.error(f"{automation_time} - {automation_info}")
            automation_data.pop(automation_time)
            rewrite_automator(write_data=automation_data)
            break  # Using break instead of continue as python doesn't like dict size change in-between a loop
        try:
            datetime.strptime(automation_time, "%I:%M %p")
        except ValueError:
            logger.error(f"Incorrect Datetime format: {automation_time}. "
                         "Datetime string should be in the format: 6:00 AM. "
                         f"Removing the key-value from {models.fileio.automation}")
            automation_data.pop(automation_time)
            rewrite_automator(write_data=automation_data)
            break  # Using break instead of continue as python doesn't like dict size change in-between a loop

        if day := automation_info.get("day"):
            today = datetime.today().strftime("%A").upper()
            if isinstance(day, list):
                if today not in [d.upper() for d in day]:
                    continue
            elif isinstance(day, str):
                day = day.upper()
                if day == "WEEKEND" and today in ["SATURDAY", "SUNDAY"]:
                    pass
                elif day == "WEEKDAY" and today in ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]:
                    pass
                elif today == day:
                    pass
                else:
                    continue

        if automation_time != datetime.now().strftime("%I:%M %p"):
            if automation_info.get("status"):
                logger.info(f"Reverting execution status flag for task: {exec_task} runs at {automation_time}")
                del automation_data[automation_time]["status"]
                rewrite_automator(write_data=automation_data)
            continue

        if automation_info.get("status"):
            continue
        exec_task = exec_task.translate(str.maketrans("", "", punctuation))  # Remove punctuations from the str
        automation_data[automation_time]["status"] = True
        rewrite_automator(write_data=automation_data)
        return exec_task
