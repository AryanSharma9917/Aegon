import os
from http import HTTPStatus
from json import JSONDecodeError
from threading import Thread
from typing import NoReturn, Union

import requests
from fastapi import APIRouter
from fastapi.responses import FileResponse

from api.modals.authenticator import OFFLINE_PROTECTOR
from api.modals.models import SpeechSynthesisModal
from api.squire.logger import logger
from modules.audio import speaker
from modules.exceptions import APIResponse, EgressErrors
from modules.models import models
from modules.utils import support

router = APIRouter()


@router.get(path='/speech-synthesis-voices', dependencies=OFFLINE_PROTECTOR)
async def speech_synthesis_voices() -> NoReturn:
    """Get all available voices in speech synthesis.

    Raises:

        - 200: If call to speech synthesis endpoint was successful.
        - 500: If call to speech synthesis fails.
    """
    try:
        response = requests.get(
            url=f"http://{models.env.speech_synthesis_host}:{models.env.speech_synthesis_port}/api/voices", timeout=3
        )
    except EgressErrors as error:
        logger.error(error)
        raise APIResponse(status_code=HTTPStatus.INTERNAL_SERVER_ERROR.real, detail=str(error))
    if response.ok:
        try:
            json_response = response.json()
        except JSONDecodeError as error:
            logger.error(error)
            raise APIResponse(status_code=HTTPStatus.INTERNAL_SERVER_ERROR.real, detail=str(error))
        available_voices = [value.get('id').replace('/', '_') for key, value in json_response.items()]
        logger.info(f"Available voices: {len(available_voices)}")
        logger.debug(available_voices)
        raise APIResponse(status_code=HTTPStatus.OK.real, detail=available_voices)
    else:
        logger.error(response.content)
        raise APIResponse(status_code=response.status_code, detail=response.content)


@router.post(path='/speech-synthesis', response_class=FileResponse, dependencies=OFFLINE_PROTECTOR)
async def speech_synthesis(input_data: SpeechSynthesisModal, raise_for_status: bool = True) -> \
        Union[FileResponse, None]:
    """Process request to convert text to speech if docker container is running.

    Args:

        - input_data: Takes the following arguments as GetText class instead of a QueryString.
        - raise_for_status: Takes a boolean flag to determine whether the result should be raised as an API response.

            - text: Text to be processed with speech synthesis.
            - timeout: Timeout for speech-synthesis API call.
            - quality: Quality of audio conversion.
            - voice: Voice model ot be used.

    Raises:

        APIResponse:
        - 404: If audio file was not found after successful response.
        - 500: If the connection to speech synthesizer fails.
        - 204: If speech synthesis file wasn't found.

    Returns:

        FileResponse:
        Audio file to be downloaded.
    """
    if not (text := input_data.text.strip()):
        logger.error('Empty requests cannot be processed.')
        if raise_for_status:
            raise APIResponse(status_code=HTTPStatus.NO_CONTENT.real, detail=HTTPStatus.NO_CONTENT.__dict__['phrase'])
        else:
            return
    if not speaker.speech_synthesizer(text=text, timeout=input_data.timeout or len(text), quality=input_data.quality,
                                      voice=input_data.voice):
        logger.error("Speech synthesis could not process the request.")
        if raise_for_status:
            raise APIResponse(status_code=HTTPStatus.INTERNAL_SERVER_ERROR.real,
                              detail=HTTPStatus.INTERNAL_SERVER_ERROR.__dict__['phrase'])
        else:
            return
    if os.path.isfile(path=models.fileio.speech_synthesis_wav):
        logger.debug(f'Speech synthesis file generated for {text!r}')
        Thread(target=support.remove_file, kwargs={'delay': 2, 'filepath': models.fileio.speech_synthesis_wav},
               daemon=True).start()
        return FileResponse(path=models.fileio.speech_synthesis_wav, media_type='application/octet-stream',
                            filename="synthesized.wav", status_code=HTTPStatus.OK.real)
    logger.error(f'File Not Found: {models.fileio.speech_synthesis_wav}')
    if raise_for_status:
        raise APIResponse(status_code=HTTPStatus.NOT_FOUND.real, detail=HTTPStatus.NOT_FOUND.__dict__['phrase'])
