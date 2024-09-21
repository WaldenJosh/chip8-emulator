# main.py

import curses
import time
import sys
from cpu import CPU  # Import the CPU class from cpu.py
from globals import status_items  # Import the status_items list from globals.py


# Function to display a status line at the bottom of the screen
def display_status_line(stdscr):
    # Get the screen dimensions
    height, width = stdscr.getmaxyx()

    # Clear the status line before updating
    stdscr.move(height - 1, 0)
    stdscr.clrtoeol()

    # Create a single string from the status items
    status_str = " | ".join(f"{key}: {value}" for key,
                            value in status_items.items())

    # Ensure the string is not longer than the screen width TODO: Add scrolling for long status strings
    if len(status_str) > width:
        status_str = status_str[:width - 1]

    # Add the status string to the bottom of the screen
    stdscr.addstr(height - 1, 0, status_str, curses.A_REVERSE)


# Main curses function
def main(stdscr):

    # Initialize ncurses
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(True)  # Make getch non-blocking
    stdscr.timeout(1)  # Set getch timeout to 100ms

    # Clear the screen
    stdscr.clear()

    # create the cpu object from the CPU class
    cpu = CPU(stdscr)

    # Check if a ROM file was provided via command line parameter
    if len(sys.argv) > 1:
        rom_path = sys.argv[1]
        cpu.load_rom(rom_path)
    else:
        status_items["rom"] = "No ROM loaded"

    # Timting variables
    cpu_cycle_duration = 1 / 60  # 500Hz CPU cycle
    screen_refresh_duration = 1 / 60  # 60Hz screen refresh

    last_cpu_cycle_time = time.time()
    last_screen_refresh_time = time.time()

    # Main loop
    frame_count = 0  # Frame counter

    while True:

        # current time
        current_time = time.time()

        # Run CPU cycles at 500Hz
        if current_time - last_cpu_cycle_time >= cpu_cycle_duration:
            # Get keystrokes TODO: Implement all the key handling
            key = stdscr.getch()
            if key == ord("q"):
                break
            cpu.run()
            last_cpu_cycle_time = current_time

        # Refresh the screen at 60Hz
        if current_time - last_screen_refresh_time >= screen_refresh_duration:
            cpu.display.display_status_line()
            cpu.display.refresh()
            last_screen_refresh_time = current_time

            # Increment the frame counter
            frame_count += 1
            if frame_count > 60:
                frame_count = 1
            status_items["frame_count"] = str(frame_count).zfill(2)

        key = stdscr.getch()
        if key != -1:
            if key == ord("q"):
                break
            chip8_key = cpu.map_key_to_chip8(key)
            if chip8_key != -1:
                cpu.keys[chip8_key] = 1  # Key pressed
            else:
                cpu.keys = [0] * 16  # Reset keys if no valid key is pressed
        else:
            cpu.keys = [0] * 16  # Reset keys if no key is pressed


# Run the main function
if __name__ == "__main__":
    curses.wrapper(main)
