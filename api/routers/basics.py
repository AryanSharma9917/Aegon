import os
from http import HTTPStatus
from typing import NoReturn

from fastapi import APIRouter
from fastapi.responses import FileResponse, RedirectResponse

from api.squire import logger
from modules.exceptions import APIResponse

router = APIRouter()


@router.get(path="/", response_class=RedirectResponse, include_in_schema=False)
async def redirect_index() -> str:
    """Redirect to docs in read-only mode.

    Returns:

        str:
        Redirects the root endpoint / url to read-only doc location.
    """
    return "/redoc"


@router.get(path="/health", include_in_schema=False)
async def health() -> NoReturn:
    """Health Check for OfflineCommunicator.

    Raises:

        - 200: For a successful health check.
    """
    raise APIResponse(status_code=HTTPStatus.OK, detail=HTTPStatus.OK.__dict__['phrase'])


@router.get(path="/favicon.ico", include_in_schema=False)
async def get_favicon() -> FileResponse:
    """Gets the favicon.ico and adds to the API endpoint.

    Returns:

        FileResponse:
        Returns the favicon.ico file as FileResponse to support the front-end.
    """
    # This logger import should not be changed to make sure the path is detected using it
    filepath = os.path.join(os.path.dirname(logger.__file__), 'favicon.ico')
    if os.path.exists(filepath):
        return FileResponse(filename=os.path.basename(filepath), path=filepath, status_code=HTTPStatus.OK.real)
    logger.logger.warning("'favicon.ico' is missing or the path is messed up. Fix this to avoid errors on front-end")
