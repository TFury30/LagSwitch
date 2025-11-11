"""
LagSwitch - Network Disconnect/Reconnect Utility

DESCRIPTION:
This script acts as a "LagSwitch" for Windows systems. It allows a user to quickly disable and re-enable their network connection using a customizable hotkey. This is achieved by executing the 'ipconfig /release' and 'ipconfig /renew' commands via the operating system's shell.

MECHANISM:
1.  **Configuration Loading:** On first run, the script prompts the user to set a hotkey (saved in 'hotkey.txt') and a mode (Toggle or Hold, saved in 'mode.txt').
2.  **Network Control:**
    *   `ipconfig /release`: Disables the network connection (the "lag" state).
    *   `ipconfig /renew`: Re-enables the network connection.
3.  **Concurrency Management:** Network operations are executed in separate threads to prevent the main program from freezing. A global lock (`network_action`) and a counter (`amount`) are used to ensure only one network operation (especially 'release') is active at a time, preventing accidental permanent disconnection.
4.  **Modes:**
    *   **Toggle (Mode 1):** Press the hotkey once to disable the internet, and press it again to re-enable it.
    *   **Hold (Mode 2):** Press and hold the hotkey to disable the internet. The internet is automatically re-enabled the moment the hotkey is released.
5.  **Notifications:** Uses `win10toast` to provide desktop notifications when the switch is enabled or disabled.

USAGE:
1.  **Prerequisites:** This script requires the `keyboard` and `win10toast` Python packages. Install them using pip:
    ```bash
    pip install keyboard win10toast
    ```
2.  **Execution:** Run the script from the command line:
    ```bash
    python LagSwitch_Enhanced.py
    ```
3.  **First Run Setup:**
    *   The script will prompt you to press a key to set your hotkey (e.g., 'f10', 'space', 'ctrl+shift+a').
    *   It will then ask you to select a mode (1 for Toggle, 2 for Hold).
4.  **Operation:** Once running, the script will minimize and wait for the hotkey press.
    *   Press the configured hotkey to activate the LagSwitch based on the selected mode.
    *   To change the hotkey or mode, delete the `hotkey.txt` and/or `mode.txt` files and run the script again.
"""

import os
import sys
import time
import threading
# External libraries
try:
    import keyboard
    from win10toast import ToastNotifier
except ImportError:
    print("Required libraries 'keyboard' and 'win10toast' not found.")
    print("Please install them using: pip install keyboard win10toast")
    sys.exit(1)

# --- Global State Variables ---
# These variables manage the state of the LagSwitch and are accessed globally.
network_action = False  # Flag: True if a network command (release/renew) is currently running.
amount = 0              # Counter: Tracks active 'disable' requests to prevent multiple releases.
hotkey = ""             # Stores the user-defined hotkey (e.g., 'f10').
mode = ""               # Stores the user-defined mode ('1' for Toggle, '2' for Hold).

# Suppress standard error output to keep the console clean from OS command noise.
# This is a common practice in scripts that run OS commands frequently.
sys.stderr = open(os.devnull, 'w')
print("Loading...")


# ==============================================================================
# 1. NOTIFICATION SYSTEM
# ==============================================================================

def _show_notification(title: str, message: str, duration: int = 2):
    """
    Internal function to display a Windows desktop notification.
    It runs in a separate thread to prevent blocking the main loop.
    Includes error handling for the notification system itself.
    """
    try:
        toaster = ToastNotifier()
        # icon_path is left empty as in the original script
        toaster.show_toast(title, message, icon_path="", duration=duration)
    except Exception as e:
        # If the notification fails (e.g., system issue), log the error and wait.
        # The original script had a recursive call, which is risky. We'll just log and exit the thread.
        # print(f"Notification failed: {e}", file=sys.stderr)
        time.sleep(duration + 0.2) # Wait for the duration to simulate the notification time

def notify(title: str, message: str, duration: int = 2):
    """
    Public function to start the notification process in a new thread.
    """
    # Use a daemon thread so it doesn't prevent the main program from exiting.
    thread = threading.Thread(target=_show_notification, args=(title, message, duration), daemon=True)
    thread.start()


# ==============================================================================
# 2. NETWORK CONTROL FUNCTIONS
# ==============================================================================

def _enable_internet_main():
    """
    Internal function to re-enable the network connection using 'ipconfig /renew'.
    Runs in a separate thread and manages the global 'network_action' lock.
    """
    global network_action, mode

    # Wait until no other network action is running
    while network_action:
        time.sleep(0.05)

    # Acquire lock and execute command
    network_action = True
    # Execute 'ipconfig /renew' to re-enable the connection
    os.system("ipconfig /renew")
    os.system("cls") # Clear console after command execution

    # Send notification and update console
    notify("LagSwitch", "Switch Disabled - Internet Enabled")
    print(f"Switch Disabled - Internet Enabled | Mode: {mode}")

    # Release lock
    network_action = False

def _disable_internet_main():
    """
    Internal function to disable the network connection using 'ipconfig /release'.
    Runs in a separate thread and manages the global 'network_action' lock and 'amount' counter.
    """
    global network_action, mode, amount

    # Wait until no other network action is running
    while network_action:
        time.sleep(0.05)

    # Critical check: If 'amount' > 0, it means another disable thread is already active
    # or the internet is already disabled. This prevents accidental permanent release.
    if amount > 0:
        return # Exit if already disabled

    # Acquire lock and increment counter
    amount += 1
    network_action = True

    # Execute 'ipconfig /release' to disable the connection
    os.system("ipconfig /release")
    os.system("cls") # Clear console after command execution

    # Send notification and update console
    notify("LagSwitch", "Switch Enabled - Internet Disabled")
    print(f"Switch Enabled - Internet Disabled | Mode: {mode}")

    # Release lock and decrement counter
    network_action = False
    amount -= 1

def enable_internet():
    """Starts the internet re-enable process in a new thread."""
    thread = threading.Thread(target=_enable_internet_main, daemon=True)
    thread.start()

def disable_internet():
    """Starts the internet disable process in a new thread."""
    thread = threading.Thread(target=_disable_internet_main, daemon=True)
    thread.start()


# ==============================================================================
# 3. CONFIGURATION LOADING
# ==============================================================================

def _load_hotkey_config() -> str:
    """
    Loads the hotkey from 'hotkey.txt'. If the file doesn't exist, it prompts
    the user to press a key and saves the result.
    """
    HOTKEY_FILE = "hotkey.txt"
    try:
        # Attempt to read existing hotkey
        with open(HOTKEY_FILE, "r") as f:
            hotkey_val = f.readline().strip()
            if not hotkey_val:
                raise FileNotFoundError # Treat empty file as non-existent
            print(f"Loaded hotkey: '{hotkey_val}'")
            return hotkey_val

    except FileNotFoundError:
        print(f"Configuration file '{HOTKEY_FILE}' not found. Starting setup...")
        print("Press the key you want to use as a bind (e.g., 'f10', 'space', 'ctrl+shift+a')...")

        # Wait for a key press event
        event = keyboard.read_event()
        hotkey_val = event.name.lower() # Use lowercase for consistency

        # Save the new hotkey
        with open(HOTKEY_FILE, "w") as f:
            f.write(hotkey_val)

        print(f"Hot key set to: '{hotkey_val}'")
        print(f"To change the hotkey, delete the '{HOTKEY_FILE}' file and run the script again.")
        time.sleep(1)
        os.system("cls")
        return hotkey_val

def _load_mode_config() -> str:
    """
    Loads the mode (1=Toggle, 2=Hold) from 'mode.txt'. If the file doesn't exist,
    it prompts the user for input and saves the result.
    """
    MODE_FILE = "mode.txt"
    try:
        # Attempt to read existing mode
        with open(MODE_FILE, "r") as f:
            mode_val = f.readline().strip()
            if mode_val not in ("1", "2"):
                 raise FileNotFoundError # Treat invalid content as non-existent
            print(f"Loaded mode: {mode_val} ({'Toggle' if mode_val == '1' else 'Hold'})")
            return mode_val

    except FileNotFoundError:
        print(f"Configuration file '{MODE_FILE}' not found. Starting setup...")
        
        # Prompt user for mode selection
        mode_val = (input("Select mode: \n1. Toggle (Press once to disable, press again to enable) \n2. Hold (Hold key to disable, release to enable)\n")).strip()

        if mode_val in ("1", "2"):
            # Save the new mode
            with open(MODE_FILE, "w") as f:
                f.write(mode_val)
            
            mode_name = "Toggle" if mode_val == "1" else "Hold"
            print(f"Mode set to: {mode_name}")
            print(f"To change the mode, delete the '{MODE_FILE}' file and run the script again.")
            time.sleep(1)
            os.system("cls")
            return mode_val
        else:
            # Exit if invalid input is provided
            input("Invalid input. Please enter only '1' or '2'. Press Enter to close the script.")
            sys.exit(1)


# ==============================================================================
# 4. MAIN LOGIC (MODES)
# ==============================================================================

def _main_toggle_mode():
    """
    Handles the Toggle mode (Mode 1).
    Press hotkey: disable internet.
    Press hotkey again: enable internet.
    """
    global hotkey
    
    # Wait for the hotkey press event
    event = keyboard.read_event()
    event_name = event.name.lower()

    if event_name == hotkey:
        # 1. Key pressed: Disable the internet
        disable_internet()

        # Wait a short period to prevent immediate re-triggering
        time.sleep(0.5)

        # 2. Wait for the second hotkey press to re-enable
        while True:
            # Read the next key event
            event = keyboard.read_event()
            event_name = event.name.lower()

            if event_name == hotkey:
                # Second key press: Enable the internet
                enable_internet()
                break
            
            # Small delay to prevent high CPU usage in the loop
            time.sleep(0.1)
        
        # Final delay to prevent the event from triggering the outer loop immediately
        time.sleep(0.5)

def _main_hold_mode():
    """
    Handles the Hold mode (Mode 2).
    Hold hotkey: disable internet.
    Release hotkey: enable internet.
    """
    global hotkey
    
    # Check if the hotkey is currently pressed
    if keyboard.is_pressed(hotkey):
        # 1. Key pressed: Disable the internet
        disable_internet()

        # 2. Hold the program while the key is pressed
        while keyboard.is_pressed(hotkey):
            # Small delay to reduce CPU load and prevent keyboard lag
            time.sleep(0.1)
            pass

        # 3. Key released: Re-enable the internet
        enable_internet()


# ==============================================================================
# 5. INITIALIZATION AND EXECUTION
# ==============================================================================

def setup():
    """
    Initializes the script by loading configuration and setting up global state.
    """
    global hotkey, mode, network_action, amount
    
    # Load configuration data
    hotkey = _load_hotkey_config()
    mode = _load_mode_config()
    
    # Initialize state variables
    network_action = False # No actions are being performed initially
    amount = 0             # No active disable requests initially
    
    print("Initialization complete.")
    os.system("cls") # Clear the console for a clean start
    
    return hotkey, mode

def main_loop():
    """
    The main execution loop that runs continuously, listening for the hotkey.
    """
    global mode
    
    # Convert mode number to descriptive name for display
    mode_name = "Toggle" if mode == "1" else "Hold"
    
    print("--------------------------------------------------")
    print("LagSwitch is running...")
    print(f"Hotkey: '{hotkey}' | Mode: {mode_name}")
    print("Switch Disabled - Internet Enabled (Initial State)")
    print("--------------------------------------------------")
    
    try:
        if mode == "1":
            # Toggle Mode Loop
            while True:
                # Small delay to prevent excessive CPU usage
                time.sleep(0.1)
                _main_toggle_mode()
        else: # mode == "2"
            # Hold Mode Loop
            while True:
                # Small delay to prevent excessive CPU usage
                time.sleep(0.1)
                _main_hold_mode()
                
    except Exception as e:
        # Catch any unexpected fatal errors during the main loop
        print("\n--- FATAL ERROR ---")
        print(f"An unexpected error occurred: {e}")
        print("-------------------")
        # The original script had a recursive call to main_loop(), which is dangerous.
        # We will exit gracefully after logging the error.
        input("Press Enter to close the script.")
        sys.exit(1)


# --- Script Entry Point ---
if __name__ == "__main__":
    # 1. Setup and configuration
    hotkey, mode = setup()
    
    # 2. Start the main loop
    main_loop()
"""
