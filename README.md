<p align="center">
  <img src="" width="371px" height="350px">
</p>
<h2 align="center">Natural Language User Interface Program with Python</h2>

[![ForTheBadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)
[![ForTheBadge built-with-swag](http://ForTheBadge.com/images/badges/built-with-swag.svg)](https://github.com/AryanSharma9917/Aegon)

![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue)

**Platform Supported**

![Generic badge](https://img.shields.io/badge/Platform-MacOS|Windows-1f425f.svg)

**Reach Out**

[![Ask Me | Anything ]

## Prerequisites
   - **MacOS** <br> _Tested on **macOS High Sierra, Mojave, Catalina, Big Sur, Monterey and Ventura***_
     - `System Preferences` → `Security & Privacy` → `Privacy`
     - Click `+` sign and add the preferred `IDE` and `Terminal` in the following sections in left pane.
       - `Microphone` - **Required** to listen and respond.
       - `Accessibility` - **Required** to use key combinations for brightness and volume controls.
       - `Camera` - **[Optional]** Required only during face recognition/detection.
       - `Automation` - **Required** to control `System Events` and other apps like Outlook and Calendar.
       - `Files and Folders` **[OR]** `Full Disk Access` - **Required** for all `FileIO` operations.

     :warning: Known Issue with <a href=https://pypi.org/project/pyttsx3/>pyttsx3 module</a> on <a href=https://www.apple.com/macos/ventura/> macOS Ventura 13.0</a>: This version of macOS does not hold the attribute `VoiceAge`. <a href=https://github.com/nateshmbhat/pyttsx3/pull/247>Workaround has been raised as a PR</a><br><br>

   - **Windows** <br> _Tested on **Windows 10**_
     - `Settings` → `Privacy`
       - `Microphone` - **Required** to listen and respond.
       - `Camera` - **[Optional]** Required only during face recognition/detection.
       - Unlike macOS, `Windows` pops a confirmation window to **Allow** or **Deny** access to files and folders.
     - Install [Anaconda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html#windows-installers), and [VisualStudio C++ BuildTools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

## Setup

> **Test Peripherals**:
>   - Camera: [camera.py](https://github.com/Aryansharma9917/Aegon/blob/master/modules/camera/camera.py)
>   - Speaker: [speak.py](https://github.com/Aryansharma9917/Aegon/blob/master/modules/speaker/speak.py)
>   - Microphone: [mic.py](https://github.com/Aryansharma9917/Aegon/blob/master/modules/microphone/mic.py)
>   - Speech Recognition: [recognizer.py](https://github.com/Aryansharma9917/Aegon/blob/master/modules/microphone/recognizer.py)

   - Download the latest stable release from [pypi](https://github.com/Aryansharma9917/Aegon/archive/master.zip) or the latest un released version from [github](https://github.com/Aryansharma9917/Aegon/archive/refs/heads/master.zip)
   - Navigate into the downloaded `aegon` or `aegon-master` directory.
   - Run the following commands in a command-line/terminal:
     1. `python3 -m venv venv` - Creates a virtual env named `venv`
     2. `source venv/bin/activate` - Activates the virtual env `venv`
     3. `which python` - Validate which python is being used. Should be the one within the virtual env `venv`
     4. `chmod +x lib/install.sh` - Makes [installation file](https://github.com/Aryansharma9917/Aegon/blob/master/lib/install.sh) as executable.
     5. `bash lib/installs.sh` - Installs the required modules based on the operating system.
     6. [`python jarvis.py`](https://git.io/JBnPz) - BOOM, you're all set, go ahead and interact with Aegon.

## ENV Variables
Environment variables are loaded from a `.env` file and validated using `pydantic`

<details>
<summary><strong>More on Environment variables</strong></summary>

- **ROOT_PASSWORD** - System password to get the system vitals and run other `sudo` commands.
- **TITLE** - Title which Jarvis should address the user by. Defaults to `sir`
- **NAME** - Name which Jarvis should address the user by. Defaults to `Aryan`
- **WAKE_WORDS** - List of wake words to initiate Jarvis' listener. Defaults to `['jarvis']` (Defaults to `['alexa']` in legacy macOS)<br>
:warning: Jarvis has limitations on the wake words as it relies on ML libraries for wake word detection.

- **VOICE_NAME** - Name of the voice supported by the OperatingSystem. Defaults to the author's favorite.
- **VOICE_RATE** - Speed/rate at which the text should be spoken. Defaults to the value from `pyttsx3` module. Typically `200`

    <details>
    <summary><strong><i>To add more voices</i></strong></summary>

    **macOS**:
    >   - System Preferences → Accessibility → Spoken Content → System voice → Manage Voices...

    **Windows**:
    >   - Settings → Time & Language → Speech → Manage voices → Add voices

    </details>

- **SENSITIVITY** - Hot word detection sensitivity. Allowed range: [0-1] Defaults to `0.5`
- **TIMEOUT** - Timeout in seconds until which the listener should wait for speech. Defaults to `3`
- **PHRASE_LIMIT** - Timeout in seconds until which the listener will remain active. Defaults to `None`
- **RECOGNIZER_SETTINGS** - A JSON object that has with customized speech recognition settings.

    <details>
    <summary><strong><i>Custom settings for speech recognition</i></strong></summary>

    These are customized according to the author's voice pitch.
    Please use [mic.py](https://github.com/Aryansharma9917/Aegon/blob/master/modules/microphone/mic.py) to figure out the suitable values in a trial and error method.

    > These settings are added (optionally), to avoid the hard coded `PHRASE_LIMIT`
    > <br>
    > Cons in using hard coded `PHRASE_LIMIT`:
    >   - Disables the listener after the set limit even the speaker is actively talking.
    >   - Listener will be active until the set limit even after the speaker has stopped talking.

    Sample settings (formatted as JSON object)
    - `RECOGNIZER_SETTINGS`: `'{"energy_threshold": 1100, "dynamic_energy_threshold": false, "pause_threshold": 2, "phrase_threshold": 0.1, "non_speaking_duration": 2}'`

    **Description**
    - `energy_threshold`: Minimum audio energy to consider for recording. Greater the value, louder the speech should be.
    - `dynamic_energy_threshold`: Change considerable audio energy threshold dynamically.
    - `pause_threshold`: Seconds of non-speaking audio before a phrase is considered complete.
    - `phrase_threshold`: Minimum seconds of speaking audio before it can be considered a phrase - values below this are ignored. This helps to filter out clicks and pops.
    - `non_speaking_duration`: Seconds of non-speaking audio to keep on both sides of the recording.

    </details>

- **LIMITED** - Boolean flag to run only the main version of `Jarvis` skipping background processes. Defaults to `False` Enforced based on the number of CPU cores.
- **CAMERA_INDEX** - Camera index that has to be used. Run [camera.py](https://github.com/Aryansharma9917/Aegon/tree/master/modules/camera/camera.py) to get the index value of each camera.
- **DEBUG** - Boolean flag to enable debug level for logging. Defaults to `False`

### Features
- **GIT_USER** - GitHub Username
- **GIT_PASS** - GitHub Token
- **WEATHER_API** - API Key from [openweathermap](https://openweathermap.org/) 
- **NEWS_API** - API Key from [newsapi](https://newsapi.org/docs/client-libraries/python)
- **MAPS_API** - API Key for maps from [Google](https://developers.google.com/maps/documentation/maps-static/get-api-key)
- **BIRTHDAY** - Birth date in the format DD-MM - Example: `24-April`
- **WOLFRAM_API_KEY** - API Key from wolfram alpha.

**Calendar/Meeting integrations**
- **ICS_URL** - Shared calendar URL to get meetings information from. Should end with `.ics`
- **EVENT_APP** - To read events from `outlook` or `calendar`. Defaults to `calendar` <br>
:bulb: &nbsp; When `calender` is used, the name of the _calendar_ within the `Calendar.app` should be **Jarvis** <br>

**Background scans [Defaults to 1 hour]**
- **SYNC_MEETINGS** - Interval in seconds to generate ``meetings`` information using `ics` URL.
- **SYNC_EVENTS** - Interval in seconds to generate ``events`` information using `calendar` or `outlook` application.

**[Wi-Fi Controls](https://github.com/Aryansharma9917/Aegon/tree/master/modules/wifi)**
- **WIFI_SSID** - SSID of the wireless connection.
- **WIFI_PASSWORD** - Password for the wireless connection.
- **CONNECTION_RETRY** - Frequency in seconds to check for an active internet connection. Defaults to 10 seconds.


**[TV](https://github.com/Aryansharma9917/Aegon/blob/master/modules/tv/tv_controls.py) controls** - Applies only for [LGWebOS](https://en.wikipedia.org/wiki/WebOS)
- **TV_CLIENT_KEY** - TV's Client key. Auto-generated when used for the first time.
- **TV_MAC** - TV's mac address. Can be single [str] or multiple [list] mac addresses (to include both wired and wireless macs).

**[Car Controls](https://github.com/Aryansharma9917/Aegon/blob/master/modules/car)** - Applies only for JLR vehicles subscribed to `InControl` application.
- **CAR_EMAIL** - Email address to log in to InControl API.
- **CAR_PASS** - Password to authenticate InControl API.
- **CAR_PIN** - InControl PIN.

**[Garage Controls](https://github.com/Aryansharma9917/Aegon/blob/master/modules/myq)** - Applies only for garages using [MyQ garage controller](https://www.myq.com/products/smart-garage-control).
- **MYQ_USERNAME** - Email address to log in to MyQ API.
- **MYQ_PASSWORD** - Password to authenticate MyQ API.

**[Telegram Bot](https://github.com/Aryansharma9917/Aegon/blob/master/executors/telegram.py) integration**
- **BOT_TOKEN** - Telegram BOT token.
- **BOT_CHAT_IDS** - UserID/ChatID for a particular user.
- **BOT_USERS** - Usernames that should have access to Jarvis.

**[OS Agnostic Voice Model](https://github.com/Aryansharma9917/Aegon/blob/master/modules/audio/speech_synthesis.py)**
- **SPEECH_SYNTHESIS_TIMEOUT** - Timeout to connect to the docker container that processes text to speech requests. <br>
    <details>
    <summary><strong><i>To enable independent speech-synthesis</i></strong></summary>

    ```shell
    docker run \
        -it \
        -p 5002:5002 \
        -e "HOME=${HOME}" \
        -v "$HOME:${HOME}" \
        -v /usr/share/ca-certificates:/usr/share/ca-certificates \
        -v /etc/ssl/certs:/etc/ssl/certs \
        -w "${PWD}" \
        --user "$(id -u):$(id -g)" \
        rhasspy/larynx
    ```

    :bulb: &nbsp; Optionally run speech synthesis on a docker container for better voices but, response might be slower. If you don't have docker installed or simply don't want to use it, set the `SPEECH_SYNTHESIS_TIMEOUT` env var to 0. This is also done automatically if failed to launch a docker container upon startup.

    </details>

---

**[Offline communicator](https://github.com/Aryansharma9917/Aegon/blob/master/executors/offline.py)**
- **OFFLINE_PORT** - Port number to initiate offline communicator. Defaults to `4483`
- **OFFLINE_PASS** - Secure phrase to authenticate offline requests. Defaults to `OfflineComm`
- **WORKERS** - Number of uvicorn workers (processes) to spin up. Defaults to `1`

**Stock Portfolio**
- **ROBINHOOD_USER** - Robinhood account username.
- **ROBINHOOD_PASS** - Robinhood account password.
- **ROBINHOOD_QR** - Robinhood login [QR code](https://robinhood.com/account/settings)

**API Features**
- **ROBINHOOD_ENDPOINT_AUTH** - Authentication token to access the robinhood portfolio which is generated every hour.
- **SURVEILLANCE_ENDPOINT_AUTH** - Token to access webcam live feed via Jarvis API.
- **SURVEILLANCE_SESSION_TIMEOUT** - Session time out for `/surveillance`. Defaults to 300 seconds.
- **STOCK_MONITOR_ENDPOINT_AUTH** - Token to add a stock price monitor. (Will soon be made `open-source`)

**Scheduler**
- **TASKS** - Runs certain tasks at certain intervals.
    <details>
    <summary><strong><i>Sample value</i></strong></summary>

    ```yaml
    [
      {"seconds": 10_800, "task": "remind me to drink water"},  # Runs every 3 hours
      {"seconds": 21_600, "task": "turn off all lights"}  # Runs every 6 hours
    ]
    ```
    </details>

- **CRONTAB** - Runs scheduled tasks using cron expressions without using actual crontab.
    <details>
    <summary><strong><i>Sample value</i></strong></summary>

    ```yaml
    [
      "0 0 * * 1-5/2 find /var/log -delete",
      "0 5 * * 1 tar -zcf /var/backups/home.tgz /home/"
    ]
    ```
    </details>

</details>

### Contacts
Aegon can send on demand notifications using a ``contacts.yaml`` file stored in ``fileio`` directory. Uses [gmail-connector](https://pypi.org/project/gmail-connector/) for SMS and email notifications.

<details>
<summary><strong><i>Setup Instructions</i></strong></summary>

> Note: Jarvis currently supports sending emails only when the ``contacts.yaml`` file is present, however phone numbers can be used directly.

```yaml
phone:
  Tony: 0123456789
  Thor: 1234567890
email:
  Eddard: ned@gmail.com
  Aegon: egg@yahoo.com
```
</details>

### Smart Devices
A source file `smart_devices.yaml` is used to store smart devices' hostnames. `Jarvis` supports [`MagicHome` lights](https://www.amazon.com/gp/product/B08C7GY43L) and `LGWebOS` TVs.

<details>
<summary><strong><i>Setup Instructions</i></strong></summary>

> Note: Jarvis currently supports only one hostname for TV but multiple for lights.

- The name used in the keys will be the identifier of those light bulbs.
- The source file (`smart_devices.yaml`) should be as following:

```yaml
bedroom:
  - 'HOSTNAMES'
hallway:
  - 'HOSTNAMES'
hallway basement:
  - 'HOSTNAMES'
kitchen:
  - 'HOSTNAMES'
living room:
  - 'HOSTNAMES'
party mode:  # Light hostnames that needs to be engaged for party mode, if not present individual lights can be enabled
  - 'HOSTNAMES'
tv: 'LGWEBOSTV'
```
</details>

### Automation Setup [Optional]
Jarvis can execute [offline compatible](https://github.com/Aryansharma9917/Aegon/blob/master/modules/offline/compatibles.py) tasks 
at pre-defined times without any user interaction. Uses an `automation.yaml` file as source which should be stored 
within the directory `fileio`

<details>
<summary><strong><i>Setup Instructions</i></strong></summary>

The YAML file should be a dictionary within a dictionary that looks like the below.

**OPTIONAL:** The key, `day` can be a `list` of days, or a `str` of a specific day or simply a `str` saying `weekday` or
`weekend` when the particular automation should be executed.

> Not having the key `day` will run the automation daily.
> Date format should match exactly as described below.

```yaml
06:00 AM:
  day: weekday  # Runs only between Monday and Friday
  task: set my bedroom lights to 50%
06:30 AM:
  day:  # Runs only on Monday, Wednesday and Friday
  - Monday
  - wednesday
  - FRIDAY
  task: set my bedroom lights to 100%
08:00 AM:  # Runs only on Saturday and Sunday
  day: weekend
  task: set my bedroom lights to 100%
09:00 PM:  # Runs daily
  task: set my bedroom lights to 5%
```
</details>

## Feature(s) Implementation
Please refer [wiki](https://github.com/Aryansharma9917/Aegon/wiki) for API usage, access controls, env variables, 
features' overview and demo videos.

## Coding Standards
Docstring format: [`Google`](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) <br>
Styling conventions: [`PEP 8`](https://www.python.org/dev/peps/pep-0008/) <br>
Clean code with pre-commit hooks: [`flake8`](https://flake8.pycqa.org/en/latest/) and 
[`isort`](https://pycqa.github.io/isort/)

## Linting
`PreCommit` will ensure linting, and the doc creation are run on every commit.

**Requirement**
<br>
`pip install --no-cache --upgrade sphinx pre-commit recommonmark`

**Usage**
<br>
`pre-commit run --all-files`

## Pypi Package
[![pypi-module](https://img.shields.io/badge/Software%20Repository-pypi-1f425f.svg)](https://packaging.python.org/tutorials/packaging-projects/)

[https://pypi.org/project/jarvis-ironman/](https://pypi.org/project/jarvis-ironman/)

