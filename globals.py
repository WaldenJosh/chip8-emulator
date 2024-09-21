# globals.py
import os
import datetime

DEBUG_MODE = True  # Set to False to disable debug logging

# Specify the log file path
log_file_path = os.path.join(os.path.dirname(__file__), "chip8_debug.log")

# Global variable to store the last log message and repetition count
last_log_message = None
repetition_count = 0


def log_debug(message):
    """
    Logs a debug message to the log file with a timestamp.
    If the message is the same as the previous log, it notes how many times it was repeated.

    :param message: The message to log
    """
    global last_log_message, repetition_count

    # Timestamp for the log entry
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if DEBUG_MODE:
        # Open the log file in append mode
        with open(log_file_path, "a") as log_file:
            if message == last_log_message:
                # Increase repetition count if the message is the same
                repetition_count += 1
            else:
                # If the message has changed and there were repetitions, note it
                if repetition_count > 0:
                    log_file.write(f"Last message repeated {
                        repetition_count} times\n")
                # Write the new message
                log_file.write(f"[{timestamp}] {message}\n")
                last_log_message = message
                repetition_count = 0


# Global dictionary to hold status items
status_items = {
    "frame_count": "0",  # Initial frame count
    "rom": "No ROM loaded",  # Initial ROM status
    "error": "",  # Initial error status
    "opcode": "",  # Initial opcode status
}
