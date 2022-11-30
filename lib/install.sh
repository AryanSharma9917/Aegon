#!/bin/bash

OSName=$(UNAME)
ver=$(python -c "import sys; print(f'{sys.version_info.major}{sys.version_info.minor}')")
echo_ver=$(python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")

echo -e '\n***************************************************************************************************'
echo "                               $OSName running python $echo_ver"
echo -e '***************************************************************************************************\n'

if [ "$ver" -ge 38 ] && [ "$ver" -le 311 ]; then
  pyaudio="PyAudio-0.2.11-cp$ver-cp$ver-win_amd64.whl"
else
  echo "Python version $echo_ver is unsupported for Jarvis. Please use any python version between 3.8.* and 3.11.*"
  exit
fi

os_independent_packages() {
    # Upgrades pip module
    python -m pip install --upgrade pip

    # Installs non version specific packages using --upgrade and --no-cache flag
    python -m pip install --no-cache --upgrade setuptools gmail-connector vpn-server

    # Get to the current directory and install the module specific packages from requirements.txt
    current_dir="$(dirname "$(realpath "$0")")"
    python -m pip install --no-cache-dir -r "$current_dir"/requirements.txt
}

download_from_ext_sources() {
    # Downloads FFmpeg for audio conversion when received voice commands from Telegram API
    curl -L https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-lgpl.zip --output ffmpeg.zip --silent && unzip ffmpeg.zip && rm -rf ffmpeg.zip && mv ffmpeg-master-latest-win64-lgpl ffmpeg

    # Downloads PyAudio's wheel file to install it on Windows
    curl https://vigneshrao.com/Jarvis/"$pyaudio" --output "$pyaudio" --silent
    pip install "$pyaudio"
    rm "$pyaudio"

    if [[ "$1" == "MOVE" ]]
      then
      mv ffmpeg ..
    fi
}

if [[ "$OSName" == "Darwin" ]]; then
    xcode-select --install
    # Looks for brew installation and installs only if brew is not found in /usr/local/bin
    brew_check=$(which brew)
    brew_condition="/usr/local/bin/brew"
    if [[ "$brew_check" != "$brew_condition" ]]; then
        echo "Installing Homebrew"
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
        else echo "Found Homebrew, skipping installation"
    fi

    # Looks for git and installs only if git is not found in /usr/bin or /usr/local/bin (if installed using brew)
    git_check=$(which git)
    git_condition_1="/usr/bin/git"
    git_condition_2="/usr/local/bin/git"
    if [[ "$git_check" == "$git_condition_1" || "$git_check" == "$git_condition_2" ]]; then
        echo "Found Git CLI, skipping installation"
        else echo "Installing Git CLI"
        brew install git
    fi

    # Packages installed using homebrew
    brew install portaudio coreutils ffmpeg lame

    # Installs the OS independent packages
    os_independent_packages

    # Mac specifics
    python -m pip install PyAudio==0.2.11 playsound==1.3.0 ftransc==7.0.3 pyobjc-framework-CoreWLAN==8.2

    # Checks current version and installs legacy pvporcupine version if macOS is older han 10.14
    base_ver="10.14"  # Versions older than Mojave (High Sierra and older versions)
    os_ver=$(sw_vers | grep ProductVersion | cut -d':' -f2 | tr -d ' ')
    if awk "BEGIN {exit !($base_ver > $os_ver)}"; then
      pip install 'pvporcupine==1.6.0'
    else
      pip install 'pvporcupine==1.9.5'
    fi

    # Install face-recognition/detection dependencies as stand alone so users aren't blocked until then
    python -m pip install opencv-python==4.4.0.44
    python -m pip install cmake==3.18.2.post1
    python -m pip install dlib==19.21.0
    python -m pip install face-recognition==1.3.0
elif [[ "$OSName" == MSYS* ]]; then
    clear
    echo "*****************************************************************************************************************"
    echo "*****************************************************************************************************************"
    echo ""
    echo "Make sure Git, Anaconda (or Miniconda) and VS C++ BuildTools are installed."
    echo ""
    echo "Refer the below links for:"
    echo "Anaconda installation: https://docs.conda.io/projects/conda/en/latest/user-guide/install/"
    echo "Miniconda installation: https://docs.conda.io/en/latest/miniconda.html#windows-installers"
    echo "VisualStudio C++ BuildTools: https://visualstudio.microsoft.com/visual-cpp-build-tools/"
    echo "Git: https://git-scm.com/download/win/"
    echo ""
    echo "*****************************************************************************************************************"
    echo "*****************************************************************************************************************"
    read -r -p "Are you sure you want to continue? <Y/N> " prompt
    if ! [[ $prompt =~ [yY](es)* ]]; then
        echo ""
        echo "***************************************************************************************************************"
        echo "Bye. Hope to see you soon."
        echo "***************************************************************************************************************"
        exit
    fi

    current_working_dir=$(pwd)
    if [[ $current_working_dir == *lib ]]
    then
      download_from_ext_sources "MOVE"
    elif [[ $current_working_dir == *Jarvis ]]
    then
      download_from_ext_sources "DO_NOT_MOVE"
    else
      echo ""
      echo "***************************************************************************************************************"
      echo "'$current_working_dir' is not the right place to trigger this script from. Please check README for instructions."
      echo "***************************************************************************************************************"
      exit
    fi

    conda install portaudio=19.6.0

    # Installs the OS independent packages
    os_independent_packages

    # Install Windows specifics
    python -m pip install pywin32==304 playsound==1.2.2 pydub==0.25.1

    # Install face-recognition/detection dependencies as stand alone so users aren't blocked until then
    python -m pip install opencv-python==4.5.5.64
    python -m pip install cmake==3.18.2.post1
    python -m pip install dlib==19.21.0
    python -m pip install face-recognition==1.3.0
else
    clear
    echo "*****************************************************************************************************************"
    echo "*****************************************************************************************************************"
    echo ""
    echo "Current Operating System: $OSName"
    echo "Jarvis is currently supported only on Mac and Windows"
    echo ""
    echo "*****************************************************************************************************************"
    echo "*****************************************************************************************************************"
fi
