# noinspection PyUnresolvedReferences
"""Module for voice changes.

>>> Voices

"""

import random
import sys
from multiprocessing import current_process

from pyttsx3.engine import Engine

from executors.word_match import word_match
from modules.audio import listener, speaker
from modules.conditions import conversation, keywords
from modules.logger.custom_logger import logger
from modules.models import models


def voice_default() -> Engine:
    """Sets voice module to default."""
    for voice in models.voices:
        if voice.name == models.env.voice_name or models.env.voice_name in voice.name:
            if current_process().name == 'MainProcess':
                logger.debug(voice.__dict__)
            models.audio_driver.setProperty("voice", voice.id)
            models.audio_driver.setProperty("rate", models.env.voice_rate)
            break
    return models.audio_driver


def voice_changer(phrase: str = None) -> None:
    """Speaks to the user with available voices and prompts the user to choose one.

    Args:
        phrase: Initiates changing voices with the model name. If none, defaults to ``Daniel``
    """
    if not phrase:
        voice_default()
        return

    choices_to_say = ["My voice module has been reconfigured. Would you like me to retain this?",
                      "Here's an example of one of my other voices. Would you like me to use this one?",
                      "How about this one?"]

    for ind, voice in enumerate(models.voices):
        models.audio_driver.setProperty("voice", models.voices[ind].id)
        speaker.speak(text=f"I am {voice.name} {models.env.title}!")
        sys.stdout.write(f"\rVoice module has been re-configured to {ind}::{voice.name}")
        if ind < len(choices_to_say):
            speaker.speak(text=choices_to_say[ind])
        else:
            speaker.speak(text=random.choice(choices_to_say))
        speaker.speak(run=True)
        if not (keyword := listener.listen()):
            voice_default()
            speaker.speak(text=f"Sorry {models.env.title}! I had trouble understanding. I'm back to my default voice.")
            return
        elif "exit" in keyword or "quit" in keyword or "Xzibit" in keyword:
            voice_default()
            speaker.speak(text=f"Reverting the changes to default voice module {models.env.title}!")
            return
        elif word_match(phrase=keyword.lower(), match_list=keywords.keywords.ok):
            speaker.speak(text=random.choice(conversation.acknowledgement))
            return
