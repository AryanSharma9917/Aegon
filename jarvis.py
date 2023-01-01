import struct
import sys
import traceback
from datetime import datetime
from typing import NoReturn

import pvporcupine
import pyaudio
from playsound import playsound

from _preexec import keywords_handler
from executors.commander import initiator
from executors.controls import exit_process, starter, terminator
from executors.internet import get_connection_info, ip_address, public_ip_info
from executors.location import write_current_location
from executors.offline import repeated_tasks
from executors.processor import clear_db, start_processes, stop_processes
from executors.system import hosted_device_info
from modules.audio import listener, speaker
from modules.exceptions import StopSignal
from modules.logger.custom_logger import custom_handler, logger
from modules.models import models
from modules.utils import shared, support
from modules.wifi.connector import ControlConnection, ControlPeripheral


def restart_checker() -> NoReturn:
    """Operations performed during internal/external request to restart."""
    if flag := support.check_restart():
        logger.info(f"Restart condition is set to {flag[0]} by {flag[1]}")
        if flag[1] == "OFFLINE":
            stop_processes()
            logger.propagate = False
            for _handler in logger.handlers:
                logger.removeHandler(hdlr=_handler)
            handler = custom_handler()
            logger.info(f"Switching to {handler.baseFilename}")
            logger.addHandler(hdlr=handler)
            starter()
            shared.processes = start_processes()
        else:
            stop_processes(func_name=flag[1])
            shared.processes[flag[1]] = start_processes(func_name=flag[1])


class Activator:
    """Awaits for the keyword ``Jarvis`` and triggers ``initiator`` when heard.

    >>> Activator

    See Also:
        - Creates an input audio stream from a microphone, monitors it, and detects the specified wake word.
        - Once detected, Jarvis triggers the ``listener.listen()`` function with an ``acknowledgement`` sound played.
        - After processing the phrase, the converted text is sent as response to ``initiator()`` with a ``return`` flag.
        - The ``should_return`` flag ensures, the user is not disturbed when accidentally woke up by wake work engine.
    """

    def __init__(self, input_device_index: int = None):
        """Initiates Porcupine object for hot word detection.

        Args:
            input_device_index: Index of Input Device to use.

        See Also:
            - Instantiates an instance of Porcupine object and monitors audio stream for occurrences of keywords.
            - A higher sensitivity results in fewer misses at the cost of increasing the false alarm rate.
            - sensitivity: Tolerance/Sensitivity level. Takes argument or env var ``sensitivity`` or defaults to ``0.5``

        References:
            - `Audio Overflow <https://people.csail.mit.edu/hubert/pyaudio/docs/#pyaudio.Stream.read>`__ handling.
        """
        logger.info(f"Initiating hot-word detector with sensitivity: {models.env.sensitivity}")
        keyword_paths = [pvporcupine.KEYWORD_PATHS[x] for x in models.env.wake_words]
        self.input_device_index = input_device_index

        self.py_audio = pyaudio.PyAudio()
        arguments = {
            "library_path": pvporcupine.LIBRARY_PATH,
            "sensitivities": models.env.sensitivity
        }
        if models.settings.legacy:
            arguments["keywords"] = models.env.wake_words
            arguments["model_file_path"] = pvporcupine.MODEL_PATH
            arguments["keyword_file_paths"] = keyword_paths
        else:
            arguments["model_path"] = pvporcupine.MODEL_PATH
            arguments["keyword_paths"] = keyword_paths

        self.detector = pvporcupine.create(**arguments)
        self.audio_stream = self.open_stream()
        self.tasks = repeated_tasks()

    def open_stream(self) -> pyaudio.Stream:
        """Initializes an audio stream.

        Returns:
            pyaudio.Stream:
            Audio stream from pyaudio.
        """
        return self.py_audio.open(
            rate=self.detector.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.detector.frame_length,
            input_device_index=self.input_device_index
        )

    def executor(self) -> NoReturn:
        """Calls the listener for actionable phrase and runs the speaker node for response."""
        logger.debug(f"Detected {models.settings.bot} at {datetime.now()}")
        playsound(sound=models.indicators.acknowledgement, block=False)
        self.py_audio.close(stream=self.audio_stream)
        if phrase := listener.listen(sound=False):
            try:
                initiator(phrase=phrase, should_return=True)
            except Exception as error:
                logger.fatal(error)
                logger.error(traceback.format_exc())
                speaker.speak(text=f"I'm sorry {models.env.title}! I ran into an unknown error. "
                                   "Please check the logs for more information.")
            speaker.speak(run=True)
        self.audio_stream = self.open_stream()

    def start(self) -> NoReturn:
        """Runs ``audio_stream`` in a forever loop and calls ``initiator`` when the phrase ``Jarvis`` is heard."""
        try:
            while True:
                sys.stdout.write(f"\rAwaiting: [{', '.join(models.env.wake_words).upper()}]")
                pcm = struct.unpack_from("h" * self.detector.frame_length,
                                         self.audio_stream.read(num_frames=self.detector.frame_length,
                                                                exception_on_overflow=False))
                result = self.detector.process(pcm=pcm)
                if models.settings.legacy:
                    if len(models.env.wake_words) == 1 and result:
                        models.settings.bot = models.env.wake_words[0]
                        self.executor()
                    elif len(models.env.wake_words) > 1 and result >= 0:
                        models.settings.bot = models.env.wake_words[result]
                        self.executor()
                else:
                    if result >= 0:
                        models.settings.bot = models.env.wake_words[result]
                        self.executor()
                if models.settings.limited:
                    continue
                keywords_handler.rewrite_keywords()
                restart_checker()
                if flag := support.check_stop():
                    logger.info(f"Stopper condition is set to {flag[0]} by {flag[1]}")
                    self.stop()
                    terminator()
        except StopSignal:
            exit_process()
            self.audio_stream = None
            self.stop()
            terminator()

    def stop(self) -> NoReturn:
        """Invoked when the run loop is exited or manual interrupt.

        See Also:
            - Terminates/Kills all the background processes.
            - Releases resources held by porcupine.
            - Closes audio stream.
            - Releases port audio resources.
        """
        for task in self.tasks:
            task.stop()
        if not models.settings.limited:
            stop_processes()
        clear_db()
        logger.info("Releasing resources acquired by Porcupine.")
        self.detector.delete()
        if self.audio_stream and self.audio_stream.is_active():
            logger.info("Closing Audio Stream.")
            self.py_audio.close(stream=self.audio_stream)
            self.audio_stream.close()
        logger.info("Releasing PortAudio resources.")
        self.py_audio.terminate()


def begin() -> NoReturn:
    """Starts main process to activate Jarvis after checking internet connection and initiating background processes."""
    logger.info(f"Current Process ID: {models.settings.pid}")
    starter()
    if ip_address() and public_ip_info():
        sys.stdout.write(f"\rINTERNET::Connected to {get_connection_info() or 'the internet'}.")
    else:
        ControlPeripheral().enable()
        if not ControlConnection().wifi_connector():
            sys.stdout.write("\rBUMMER::Unable to connect to the Internet")
            speaker.speak(text=f"I was unable to connect to the internet {models.env.title}! "
                               "Please check your connection.", run=True)
    sys.stdout.write(f"\rCurrent Process ID: {models.settings.pid}\tCurrent Volume: {models.env.volume}")
    shared.hosted_device = hosted_device_info()
    if not models.settings.limited:
        shared.processes = start_processes()
    write_current_location()
    Activator().start()


if __name__ == '__main__':
    begin()
