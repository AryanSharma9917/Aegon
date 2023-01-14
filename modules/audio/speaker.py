# noinspection PyUnresolvedReferences
"""Module for speaker and voice options.

>>> Speaker

"""
import os
import re
import sys
from datetime import datetime
from threading import Thread
from typing import NoReturn, Union

import requests
import yaml
from playsound import playsound

from modules.conditions import conversation, keywords
from modules.exceptions import EgressErrors
from modules.logger.custom_logger import logger
from modules.models import models
from modules.utils import shared

KEYWORDS = [__keyword for __keyword in dir(keywords) if not __keyword.startswith('__')]
CONVERSATION = [__conversation for __conversation in dir(conversation) if not __conversation.startswith('__')]
FUNCTIONS_TO_TRACK = KEYWORDS + CONVERSATION


def speech_synthesizer(text: str, timeout: Union[int, float] = models.env.speech_synthesis_timeout,
                       quality: str = "high", voice: str = "en-us_northern_english_male-glow_tts") -> bool:
    """Makes a post call to docker container for speech synthesis.

    Args:
        text: Takes the text that has to be spoken as an argument.
        timeout: Time to wait for the docker image to process text-to-speech request.
        quality: Quality at which the conversion is to be done.
        voice: Voice for speech synthesis.

    Returns:
        bool:
        A boolean flag to indicate whether speech synthesis has worked.
    """
    logger.info(f"Request for speech synthesis: {text}")
    if time_in_str := re.findall(r'(\d+:\d+\s?(?:AM|PM|am|pm:?))', text):
        for t_12 in time_in_str:
            t_24 = datetime.strftime(datetime.strptime(t_12, "%I:%M %p"), "%H:%M")
            logger.info(f"Converted {t_12} -> {t_24}")
            text = text.replace(t_12, t_24)
    if 'IP' in text.split():
        ip_new = '-'.join([i for i in text.split(' ')[-1]]).replace('-.-', ', ')  # 192.168.1.1 -> 1-9-2, 1-6-8, 1, 1
        text = text.replace(text.split(' ')[-1], ip_new).replace(' IP ', ' I.P. ')
    try:
        response = requests.post(
            url=f"http://{models.env.speech_synthesis_host}:{models.env.speech_synthesis_port}/api/tts",
            headers={"Content-Type": "text/plain"}, params={"voice": voice, "quality": quality}, data=text,
            verify=False, timeout=timeout
        )
        if response.ok:
            with open(file=models.fileio.speech_synthesis_wav, mode="wb") as file:
                file.write(response.content)
            return True
        logger.error(f"{response.status_code}::"
                     f"http://{models.env.speech_synthesis_host}:{models.env.speech_synthesis_port}/api/tts")
        return False
    except UnicodeError as error:
        logger.error(error)
    except EgressErrors as error:
        logger.error(error)
        logger.info("Disabling speech synthesis")
        models.env.speech_synthesis_timeout = 0


def speak(text: str = None, run: bool = False, block: bool = True) -> NoReturn:
    """Calls ``audio_driver.say`` to speak a statement from the received text.

    Args:
        text: Takes the text that has to be spoken as an argument.
        run: Takes a boolean flag to choose whether to run the ``audio_driver.say`` loop.
        block: Takes a boolean flag to wait other tasks while speaking. [Applies only for larynx running on docker]
    """
    caller = sys._getframe(1).f_code.co_name  # noqa
    if text:
        text = text.replace('\n', '\t').strip()
        shared.text_spoken = text
        if shared.called_by_offline:
            shared.offline_caller = caller
            return
        logger.info(f'Speaker called by: {caller!r}')
        logger.info(f'Response: {text}')
        sys.stdout.write(f"\r{text}")
        if models.env.speech_synthesis_timeout and \
                speech_synthesizer(text=text) and \
                os.path.isfile(models.fileio.speech_synthesis_wav):
            playsound(sound=models.fileio.speech_synthesis_wav, block=block)
            os.remove(models.fileio.speech_synthesis_wav)
        else:
            models.audio_driver.say(text=text)
    if run:
        models.audio_driver.runAndWait()
    Thread(target=frequently_used, kwargs={"function_name": caller}).start() if caller in FUNCTIONS_TO_TRACK else None


def frequently_used(function_name: str) -> NoReturn:
    """Writes the function called and the number of times into a yaml file.

    Args:
        function_name: Name of the function that called the speaker.

    See Also:
        - This function does not have purpose, but to analyze and re-order the conditions' module at a later time.
    """
    if os.path.isfile(models.fileio.frequent):
        try:
            with open(models.fileio.frequent) as file:
                data = yaml.load(stream=file, Loader=yaml.FullLoader) or {}
        except yaml.YAMLError as error:
            data = {}
            logger.error(error)
        if data.get(function_name):
            data[function_name] += 1
        else:
            data[function_name] = 1
    else:
        data = {function_name: 1}
    with open(models.fileio.frequent, 'w') as file:
        yaml.dump(data={k: v for k, v in sorted(data.items(), key=lambda x: x[1], reverse=True)},
                  stream=file, sort_keys=False)
