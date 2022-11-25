# Aegon
## Aegon is an personal assistant project which is created in order to make it a Windows application for performing many tasks without touching the system physically.

<p align="center">
  <img src="https://github.com/AryanSharma9917/Aegon/blob/main/indicators/AEGON.png" width="371px" height="350px">
</p>
<h2 align="center">Natural Language User Interface Program with Python</h2>

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

   - **Windows** <br> _Tested on **Windows 11**_
     - `Settings` → `Privacy`
       - `Microphone` - **Required** to listen and respond.
       - `Camera` - **[Optional]** Required only during face recognition/detection.
       - Unlike macOS, `Windows` pops a confirmation window to **Allow** or **Deny** access to files and folders.
     - Install [Anaconda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html#windows-installers), and [VisualStudio C++ BuildTools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

## Setup

> **Test Peripherals**:
>   - Camera: [camera.py](https://github.com/AryanSharma9917/Aegon/tree/main/Modules/Camera/camera.py)
>   - Speaker: [speak.py](https://github.com/AryanSharma9917/Aegon/blob/main/Modules/speaker/speaker.py)
>   - Microphone: [mic.py](https://github.com/AryanSharma9917/Aegon/tree/main/Modules/microphone)
<!-- >   - Speech Recognition: [recognizer.py](https://github.com/AryanSharma9917/Aegon/tree/main/Modules) -->

   <!-- - Download the latest stable release from [pypi](https://github.com/Aryansharma9917/Jarvis/archive/master.zip)
   - Navigate into the downloaded `jarvis` or `jarvis-master` directory.
   - Run the following commands in a command-line/terminal:
     1. `python3 -m venv venv` - Creates a virtual env named `venv`
     2. `source venv/bin/activate` - Activates the virtual env `venv`
     3. `which python` - Validate which python is being used. Should be the one within the virtual env `venv`
     4. `chmod +x lib/install.sh` - Makes [installation file](https://github.com/Aryansharma9917/Jarvis/blob/master/lib/install.sh) as executable.
     5. `bash lib/installs.sh` - Installs the required modules based on the operating system.
     6. [`python jarvis.py`](https://git.io/JBnPz) - BOOM, you're all set, go ahead and interact with Jarvis. -->

## ENV Variables
Environment variables are loaded from a `.env` file and validated using `pydantic`

<details>
<summary><strong>More on Environment variables</strong></summary>

- **ROOT_PASSWORD** - System password to get the system vitals and run other `sudo` commands.
- **TITLE** - Title which Jarvis should address the user by. Defaults to `sir`
- **NAME** - Name which Jarvis should address the user by. Defaults to `Vignesh`
- **WAKE_WORDS** - List of wake words to initiate Jarvis' listener. Defaults to `['Aegon']` (Defaults to `['alexa']` in legacy macOS)<br>
:warning: Aegon has limitations on the wake words as it relies on ML libraries for wake word detection.

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
    Please use [mic.py](https://github.com/thevickypedia/Jarvis/blob/master/modules/microphone/mic.py) to figure out the suitable values in a trial and error method.

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

- 
- **DEBUG** - Boolean flag to enable debug level for logging. Defaults to `False`

### Features
- **GIT_USER** - GitHub Username
- **GIT_PASS** - GitHub Token
- **WEATHER_API** - API Key from [openweathermap](https://openweathermap.org/) 
- **NEWS_API** - API Key from [newsapi](https://newsapi.org/docs/client-libraries/python)
- **MAPS_API** - API Key for maps from [Google](https://developers.google.com/maps/documentation/maps-static/get-api-key)
- **BIRTHDAY** - Birth date in the format DD-MM - Example: `24-April`
- **WOLFRAM_API_KEY** - API Key from wolfram alpha.



**iOS integrations**
- **ICLOUD_USER** - iCloud account username/email.
- **ICLOUD_PASS** - iCloud account password.
- **ICLOUD_RECOVERY** - Recovery phone number to activate lost mode on a target device - Example: `+11234567890`
- **PHONE_NUMBER** - To send SMS from Jarvis - Example: `+11234567890`



### Contacts
Jarvis can send on demand notifications using a ``contacts.yaml`` file stored in ``fileio`` directory. Uses [gmail-connector](https://pypi.org/project/gmail-connector/) for SMS and email notifications.

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
Aegon can execute [offline compatible](https://github.com/thevickypedia/Jarvis/blob/master/modules/offline/compatibles.py) tasks 
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
Please refer [wiki](https://github.com/thevickypedia/Jarvis/wiki) for API usage, access controls, env variables, 
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

## Runbook
[![made-with-sphinx-doc](https://img.shields.io/badge/Code%20Docs-Sphinx-1f425f.svg)](https://www.sphinx-doc.org/en/master/man/sphinx-autogen.html)
