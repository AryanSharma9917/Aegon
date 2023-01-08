# noinspection PyUnresolvedReferences
"""This is a space where all the validated environment variables are loaded and evalued as per requirements.

>>> Models

"""

import os
from multiprocessing import current_process
from typing import NoReturn, Union

import cv2
import pvporcupine
import requests
from pydantic import PositiveInt

from api.squire.scheduler import rh_cron_schedule, sm_cron_schedule
from modules.camera.camera import Camera
from modules.crontab.expression import CronExpression
from modules.database import database
from modules.exceptions import (CameraError, EgressErrors, InvalidEnvVars,
                                MissingEnvVars)
from modules.models.classes import (Indicators, RecognizerSettings,
                                    audio_driver, env, fileio, settings)

# Shared across other modules
voices: Union[list, object] = audio_driver.getProperty("voices")
indicators = Indicators()
# TABLES to be created in `fileio.base_db`
TABLES = {
    env.event_app: ("info", "date"),
    "ics": ("info", "date"),
    "stopper": ("flag", "caller"),
    "restart": ("flag", "caller"),
    "children": ("meetings", "events", "crontab", "party", "guard", "surveillance"),
    "vpn": ("state",),
    "party": ("pid",),
    "guard": ("state",),
}
KEEP_TABLES = ("vpn", "party")  # TABLES to keep from `fileio.base_db`


def _main_process_validations() -> NoReturn:
    """Validations that should happen only when the main process is triggered."""
    voice_names = [__voice.name for __voice in voices]
    if not env.voice_name:
        if settings.os == "Darwin":
            env.voice_name = "Daniel"
        elif settings.os == "Windows":
            env.voice_name = "David"
        elif settings.os == "Linux":
            env.voice_name = "english-us"
    elif env.voice_name not in voice_names:
        raise InvalidEnvVars(
            f"{env.voice_name!r} is not available.\nAvailable voices are: {', '.join(voice_names)}"
        )

    if not env.recognizer_settings and not env.phrase_limit:
        env.recognizer_settings = RecognizerSettings()  # Default override when phrase limit is not available

    if settings.legacy:
        pvporcupine.KEYWORD_PATHS = {}
        pvporcupine.MODEL_PATH = os.path.join(os.path.dirname(pvporcupine.__file__),
                                              'lib/common/porcupine_params.pv')
        pvporcupine.LIBRARY_PATH = os.path.join(os.path.dirname(pvporcupine.__file__),
                                                'lib/mac/x86_64/libpv_porcupine.dylib')
        keyword_files = os.listdir(os.path.join(os.path.dirname(pvporcupine.__file__),
                                                'resources/keyword_files/mac/'))

        for x in keyword_files:  # Iterates over the available flash files, to override the class
            pvporcupine.KEYWORD_PATHS[x.split('_')[0]] = os.path.join(os.path.dirname(pvporcupine.__file__),
                                                                      f'resources/keyword_files/mac/{x}')

    for keyword in env.wake_words:
        if not pvporcupine.KEYWORD_PATHS.get(keyword) or not os.path.isfile(pvporcupine.KEYWORD_PATHS[keyword]):
            raise InvalidEnvVars(
                f"Detecting {keyword!r} is unsupported!\n"
                f"Available keywords are: {', '.join(list(pvporcupine.KEYWORD_PATHS.keys()))}"
            )

    # If sensitivity is an integer or float, converts it to a list
    if isinstance(env.sensitivity, float) or isinstance(env.sensitivity, PositiveInt):
        env.sensitivity = [env.sensitivity] * len(env.wake_words)

    # Create all necessary DB tables during startup
    db = database.Database(database=fileio.base_db)
    for table, column in TABLES.items():
        db.create_table(table_name=table, columns=column)


def _global_validations() -> NoReturn:
    """Validations that should happen for all processes including parent and child."""
    # Validate root password present for linux systems
    if settings.os == "Linux":
        if not env.root_password:
            raise MissingEnvVars(
                "Linux requires the host machine's password to be set as the env var: "
                "ROOT_PASSWORD due to terminal automations."
            )

    if env.website:
        env.website = env.website.lstrip(f"{env.website.scheme}://")

    if not all((env.alt_gmail_user, env.alt_gmail_pass)):
        env.alt_gmail_user = env.gmail_user
        env.alt_gmail_pass = env.gmail_pass

    if not all((env.open_gmail_user, env.open_gmail_pass)):
        env.open_gmail_user = env.alt_gmail_user
        env.open_gmail_pass = env.alt_gmail_pass

    # Note: Pydantic validation for ICS_URL can be implemented using regex=".*ics$"
    # However it will NOT work in this use case, since the type hint is HttpUrl
    if env.ics_url and not env.ics_url.endswith('.ics'):
        raise InvalidEnvVars(
            "'ICS_URL' should end with .ics"
        )

    if env.speech_synthesis_port == env.offline_port:
        raise InvalidEnvVars(
            "Speech synthesizer and offline communicator cannot run simultaneously on the same port number."
        )

    if all([env.robinhood_user, env.robinhood_pass, env.robinhood_pass]):
        env.crontab.append(rh_cron_schedule(extended=True))
    env.crontab.append(sm_cron_schedule())

    if env.limited:  # Forces limited version if env var is set, otherwise it is enforced based on the number of cores
        settings.limited = True
    if env.limited is False:  # If env var is set as False to brute force full version on a device with < 4 processors
        settings.limited = False

    # Validates crontab expression if provided
    for expression in env.crontab:
        CronExpression(expression)

    # Validate if able to read camera only if a camera env var is set,
    try:
        if env.camera_index is None:
            cameras = []
        else:
            cameras = Camera().list_cameras()
    except CameraError:
        cameras = []
    if cameras:
        if env.camera_index >= len(cameras):
            raise InvalidEnvVars(
                f"Camera index # {env.camera_index} unavailable.\n"
                "Camera index cannot exceed the number of available cameras.\n"
                f"{len(cameras)} available cameras: {', '.join([f'{i}: {c}' for i, c in enumerate(cameras)])}"
            )
    else:
        env.camera_index = None

    if env.camera_index is not None:
        cam = cv2.VideoCapture(env.camera_index)
        if cam is None or not cam.isOpened() or cam.read() == (False, None):
            raise CameraError(f"Unable to read the camera - {cameras[env.camera_index]}")
        cam.release()

    # Validate voice for speech synthesis
    try:
        response = requests.get(url=f"http://{env.speech_synthesis_host}:{env.speech_synthesis_port}/api/voices",
                                timeout=(1, 1))  # Set connect and read timeout to bare minimum
        if response.ok:
            available_voices = [value.get('id').replace('/', '_') for key, value in response.json().items()]
            if env.speech_synthesis_voice not in available_voices:
                raise InvalidEnvVars(
                    f"{env.speech_synthesis_voice} is not available.\n"
                    f"Available Voices for Speech Synthesis: {', '.join(available_voices).replace('/', '_')}"
                )
    except EgressErrors:
        pass


_global_validations()
if settings.bot == "jarvis" and current_process().name == "MainProcess":
    _main_process_validations()
