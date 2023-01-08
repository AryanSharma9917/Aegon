import mimetypes
import os
from datetime import datetime
from http import HTTPStatus
from threading import Thread
from typing import NoReturn

import jinja2
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from gmailconnector.send_email import SendEmail

from api.modals.authenticator import ROBINHOOD_PROTECTOR
from api.modals.settings import robinhood
from api.squire import timeout_otp
from api.squire.logger import logger
from modules.exceptions import APIResponse
from modules.models import models
from modules.templates import templates
from modules.utils import util

router = APIRouter()

# Conditional endpoint: Condition matches without env vars during docs generation
if not os.getcwd().endswith("Jarvis") or all([models.env.robinhood_user, models.env.robinhood_pass,
                                              models.env.robinhood_pass, models.env.robinhood_endpoint_auth]):
    @router.post(path="/robinhood-authenticate", dependencies=ROBINHOOD_PROTECTOR)
    async def authenticate_robinhood() -> NoReturn:
        """Authenticates the request and generates single use token.

        Raises:

            APIResponse:
            - 200: If initial auth is successful and single use token is successfully sent via email.
            - 503: If failed to send the single use token via email.

        See Also:

            If basic auth (stored as an env var robinhood_endpoint_auth) succeeds:

            - Sends a token for MFA via email.
            - Also stores the token in the Robinhood object which is verified in the /investment endpoint.
            - The token is nullified in the object as soon as it is verified, making it single use.
        """
        mail_obj = SendEmail(gmail_user=models.env.alt_gmail_user, gmail_pass=models.env.alt_gmail_pass)
        auth_stat = mail_obj.authenticate
        if not auth_stat.ok:
            raise APIResponse(status_code=HTTPStatus.SERVICE_UNAVAILABLE.real, detail=auth_stat.body)
        robinhood.token = util.keygen_uuid(length=16)
        rendered = jinja2.Template(templates.email.one_time_passcode).render(ENDPOINT='robinhood',
                                                                             TOKEN=robinhood.token,
                                                                             EMAIL=models.env.recipient)
        mail_stat = mail_obj.send_email(recipient=models.env.recipient, sender='Jarvis API',
                                        subject=f"Robinhood Token - {datetime.now().strftime('%c')}",
                                        html_body=rendered)
        if mail_stat.ok:
            Thread(target=timeout_otp.reset_robinhood, args=(300,)).start()
            raise APIResponse(status_code=HTTPStatus.OK.real,
                              detail="Authentication success. Please enter the OTP sent via email:")
        else:
            logger.error(mail_stat.json())
            raise APIResponse(status_code=HTTPStatus.SERVICE_UNAVAILABLE.real, detail=mail_stat.body)

# Conditional endpoint: Condition matches without env vars during docs generation
if not os.getcwd().endswith("Jarvis") or all([models.env.robinhood_user, models.env.robinhood_pass,
                                              models.env.robinhood_pass, models.env.robinhood_endpoint_auth]):
    @router.get(path="/investment", response_class=HTMLResponse)
    async def robinhood_path(request: Request, token: str = None) -> HTMLResponse:
        """Serves static file.

        Args:

            - request: Takes the Request class as an argument.
            - token: Takes custom auth token as an argument.

        Raises:

            APIResponse:
            - 403: If token is null.
            - 404: If the HTML file is not found.
            - 417: If token doesn't match the auto-generated value.

        Returns:

            HTMLResponse:
            Renders the html page.

        See Also:

            - This endpoint is secured behind single use token sent via email as MFA (Multi-Factor Authentication)
            - Initial check is done by the function authenticate_robinhood behind the path "/robinhood-authenticate"
            - Once the auth succeeds, a one-time usable hex-uuid is generated and stored in the Robinhood object.
            - This UUID is sent via email to the env var RECIPIENT, which should be entered as query string.
            - The UUID is deleted from the object as soon as the argument is checked for the first time.
            - Page refresh is useless because the value in memory is cleared as soon as it is authed once.
        """
        logger.debug(f"Connection received from {request.client.host} via {request.headers.get('host')} using "
                     f"{request.headers.get('user-agent')}")
        if not token:
            raise APIResponse(status_code=HTTPStatus.UNAUTHORIZED.real,
                              detail=HTTPStatus.UNAUTHORIZED.__dict__['phrase'])
        if token == robinhood.token:
            robinhood.token = None
            if not os.path.isfile(models.fileio.robinhood):
                raise APIResponse(status_code=HTTPStatus.NOT_FOUND.real, detail='Static file was not found on server.')
            with open(models.fileio.robinhood) as static_file:
                html_content = static_file.read()
            content_type, _ = mimetypes.guess_type(html_content)
            return HTMLResponse(status_code=HTTPStatus.TEMPORARY_REDIRECT.real,
                                content=html_content, media_type=content_type)  # serves as a static webpage
        else:
            raise APIResponse(status_code=HTTPStatus.EXPECTATION_FAILED.real,
                              detail='Requires authentication since endpoint uses single-use token.')
