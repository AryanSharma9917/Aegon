import json
import platform
from enum import Enum
from typing import Dict, Iterable, Union

import pyaudio

from modules.exceptions import no_alsa_err

if platform.system() == "Linux":
    with no_alsa_err():
        audio_engine = pyaudio.PyAudio()
else:
    audio_engine = pyaudio.PyAudio()
# audio_engine.open(output_device_index=6, output=True, channels=1, format=pyaudio.paInt16, rate=16000)
_device_range = audio_engine.get_device_count()


class ChannelType(str, Enum):
    """Allowed values for channel types.

    >>> ChannelType

    """

    input_channels: str = 'maxInputChannels'
    output_channels: str = 'maxOutputChannels'


channel_type = ChannelType


def get_audio_devices(channels: str) -> Iterable[Dict[str, Union[str, int, float]]]:
    """Iterates over all devices and yields the device that has input channels.

    Args:
        channels: Takes an argument to determine whether to yield input or output channels.

    Yields:
        Iterable:
        Yields a dictionary with all the input devices available.
    """
    for index in range(_device_range):
        device_info = audio_engine.get_device_info_by_index(device_index=index)
        if device_info.get(channels, 0) > 0:
            yield device_info


if __name__ == '__main__':
    print(json.dumps(list(get_audio_devices(channels=channel_type.input_channels)), indent=2))
    print(json.dumps(list(get_audio_devices(channels=channel_type.output_channels)), indent=2))
