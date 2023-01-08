import asyncio
from threading import Thread
from typing import Any, Callable, NoReturn

from pymyq.errors import AuthenticationError, InvalidCredentialsError, MyQError

from modules.audio import speaker
from modules.exceptions import CoverNotOnline, NoCoversFound
from modules.logger.custom_logger import logger
from modules.models import models
from modules.myq import myq
from modules.utils import support


class AsyncThread(Thread):
    """Runs asynchronosly using threading.

    >>> AsyncThread

    """

    def __init__(self, func: Callable, args: Any, kwargs: Any):
        """Initiates ``AsyncThread`` object as a super class.

        Args:
            func: Function that has to be triggered.
            args: Arguments.
            kwargs: Keyword arguments.
        """
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.result = None
        super().__init__()

    def run(self) -> NoReturn:
        """Initiates ``asyncio.run`` with arguments passed."""
        self.result = asyncio.run(self.func(*self.args, **self.kwargs))


def run_async(func: Callable, *args: Any, **kwargs: Any) -> Any:
    """Checks if an existing loop is running in asyncio and triggers the loop with or without a thread accordingly.

    Args:
        func: Function that has to be triggered.
        args: Arguments.
        kwargs: Keyword arguments.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        thread = AsyncThread(func, args, kwargs)
        thread.start()
        thread.join()
        return thread.result
    else:
        return asyncio.run(func(*args, **kwargs))


def garage(phrase: str) -> NoReturn:
    """Handler for the garage door controller.

    Args:
        phrase: Takes the recognized phrase as an argument.
    """
    if all([models.env.myq_username, models.env.myq_password]):
        phrase = phrase.lower()
    else:
        support.no_env_vars()
        return

    logger.info("Getting status of the garage door.")
    try:
        status = run_async(func=myq.garage_controller, execute=myq.operation.STATE, phrase=phrase)
    except InvalidCredentialsError as error:
        logger.error(error)
        speaker.speak(text=f"I'm sorry {models.env.title}! Your credentials do not match.")
        return
    except AuthenticationError as error:
        logger.error(error)
        speaker.speak(text=f"I'm sorry {models.env.title}! There was an authentication error.")
        return
    except MyQError as error:
        logger.error(error)
        speaker.speak(text=f"I wasn't able to connect to the module {models.env.title}! "
                           "Please check the logs for more information.")
        return
    except NoCoversFound as error:
        logger.error(error)
        speaker.speak(text=f"No garage doors were found in your MyQ account {models.env.title}! "
                           "Please check your MyQ account and add a garage door name to control it.")
        return
    except CoverNotOnline as error:
        logger.error(error)
        speaker.speak(text=f"I'm sorry {models.env.title}! Your {error.device} is not online!")
        return

    logger.info(status)
    if myq.operation.OPEN in phrase:
        if status['state']['door_state'] == myq.operation.OPEN:
            speaker.speak(text=f"Your {status['name']} is already open {models.env.title}!")
            return
        elif status['state']['door_state'] == myq.operation.OPENING:
            speaker.speak(text=f"Your {status['name']} is currently opening {models.env.title}!")
            return
        elif status['state']['door_state'] == myq.operation.CLOSING:
            speaker.speak(text=f"Your {status['name']} is currently closing {models.env.title}! "
                               "You may want to retry after a minute or two!")
            return
        logger.info(f"Opening {status['name']}.")
        response = run_async(func=myq.garage_controller, execute=myq.operation.OPEN, phrase=phrase)
        speaker.speak(text=response)
    elif myq.operation.CLOSE in phrase:
        if status['state']['door_state'] == myq.operation.CLOSED:
            speaker.speak(text=f"Your {status['name']} is already closed {models.env.title}!")
            return
        elif status['state']['door_state'] == myq.operation.CLOSING:
            speaker.speak(text=f"Your {status['name']} is currently closing {models.env.title}!")
            return
        elif status['state']['door_state'] == myq.operation.OPENING:
            speaker.speak(text=f"Your {status['name']} is currently opening {models.env.title}! "
                               "You may want to try to after a minute or two!")
            return
        logger.info(f"Closing {status['name']}.")
        response = run_async(func=myq.garage_controller, execute=myq.operation.CLOSE, phrase=phrase)
        speaker.speak(text=response)
    else:
        logger.info(f"{status['name']}: {status['state']['door_state']}")
        speaker.speak(text=f"Your {status['name']} is currently {status['state']['door_state']} {models.env.title}! "
                           f"What do you want me to do to your {status['name']}?")
