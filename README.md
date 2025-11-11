# LagSwitch: Hotkey-Controlled Network Disconnect Utility

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![OS](https://img.shields.io/badge/OS-Windows-0078D6.svg)](https://www.microsoft.com/windows/)
[![License](https://img.shields.io/badge/License-Unspecified-lightgrey.svg)](LICENSE)

## 📝 Overview

This Python script, often referred to as a "LagSwitch," provides a quick and easy way to temporarily disable and re-enable your network connection on a Windows system using a customizable hotkey. This is achieved by executing the native Windows commands `ipconfig /release` and `ipconfig /renew`.

The primary use case is for testing network resilience or for specific scenarios where temporary network interruption is required.

## ✨ Features

*   **Hotkey Control:** Quickly activate and deactivate the network switch with a single, user-defined key press.
*   **Two Modes of Operation:** Supports **Toggle** (press once to activate, press again to deactivate) and **Hold** (hold the key to activate, release to deactivate) modes.
*   **Windows Notifications:** Provides desktop notifications using `win10toast` when the switch state changes.
*   **Persistent Configuration:** Saves your chosen hotkey and mode to local files (`hotkey.txt` and `mode.txt`) for easy reuse.
*   **Thread-Safe Operations:** Network commands run in separate threads to prevent the main application from freezing.

## ⚠️ Prerequisites

This script is designed exclusively for **Windows** operating systems, as it relies on the `ipconfig` command.

You must have **Python 3.x** installed.

### Required Python Libraries

The script requires the following libraries, which can be installed via `pip`:

*   `keyboard`: For reading global hotkey events.
*   `win10toast`: For displaying native Windows desktop notifications.

## 🚀 Installation

1.  **Clone the repository (or download the script):**
    ```bash
    git clone https://github.com/TFury30/LagSwitch.git
    cd LagSwitch
    ```
2.  **Install the required dependencies:**
    ```bash
    pip install keyboard win10toast
    ```

## 💻 Usage

1.  **Run the script:**
    ```bash
    python LagSwitch.py
    ```

2.  **First-Time Setup:**
    *   **Hotkey Configuration:** The script will prompt you to press the key you wish to use as your hotkey (e.g., `f10`, `space`, `ctrl+shift+a`). This key will be saved in `hotkey.txt`.
    *   **Mode Selection:** You will then be asked to select a mode: `1` for **Toggle** or `2` for **Hold**. This choice will be saved in `mode.txt`.

3.  **Operation:**
    *   Once the setup is complete, the console will clear and display the running status.
    *   The script will now run in the background, listening for your configured hotkey.
    *   Use the hotkey according to the mode you selected.

### Changing Configuration

To change your hotkey or mode, simply delete the corresponding configuration file(s) and run the script again:

```bash
# To change the hotkey
del hotkey.txt

# To change the mode
del mode.txt
```

## ⚙️ Modes of Operation

| Mode | Description | Mechanism |
| :--- | :--- | :--- |
| **1: Toggle** | Press the hotkey once to disable the internet, and press it again to re-enable it. | The script waits for two distinct key presses to cycle the network state. |
| **2: Hold** | Press and hold the hotkey to disable the internet. The internet is automatically re-enabled the moment the hotkey is released. | The script continuously checks if the key is held down. |

## ⚖️ Disclaimer

This tool works by executing `ipconfig /release` and `ipconfig /renew` via the command line. Use of this script is entirely at your own risk. The author is not responsible for any damage, loss of data, or consequences resulting from the use of this software.

**Please use this tool responsibly and ethically.**
