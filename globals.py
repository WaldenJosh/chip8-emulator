# globals.py
import os
import datetime

DEBUG_MODE = True  # Set to False to disable debug logging

# Specify the log file path
log_file_path = os.path.join(os.path.dirname(__file__), "chip8_debug.log")


def log_debug(message):
    """
    Logs a debug message to the log file with a timestamp.

    :param message: The message to log
    """
    # Timestamp for the log entry
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if DEBUG_MODE:
        # Open the log file in append mode
        with open(log_file_path, "a") as log_file:
            # Write the message with the timestamp
            log_file.write(f"[{timestamp}] {message}\n")


# Global dictionary to hold status items
status_items = {
    "frame_count": "0",  # Initial frame count
    "rom": "No ROM loaded",  # Initial ROM status
    "error": "",  # Initial error status
    "opcode": "",  # Initial opcode status
}
