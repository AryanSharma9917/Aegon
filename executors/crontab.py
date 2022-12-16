import os
import subprocess
from typing import NoReturn

from modules.logger import config

LOG_FILE = os.path.join('logs', 'cron_%d-%m-%Y.log')  # Used by api functions that run on cron schedule


def crontab_executor(statement: str) -> NoReturn:
    """Executes a cron statement.

    Args:
        statement: Cron statement to be executed.
    """
    filename = config.multiprocessing_logger(filename=LOG_FILE)
    with open(filename, 'a') as file:
        file.write('\n')
        try:
            subprocess.call(statement, shell=True, stdout=file, stderr=file)
        except (subprocess.CalledProcessError, subprocess.SubprocessError, Exception) as error:
            if isinstance(error, subprocess.CalledProcessError):
                result = error.output.decode(encoding='UTF-8').strip()
                file.write(f"[{error.returncode}]: {result}")
            else:
                file.write(error)
