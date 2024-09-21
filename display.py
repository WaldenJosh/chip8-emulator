# display.py
import curses
from globals import status_items


class Display:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.width = 64
        self.height = 32
        self.screen = [[0] * self.width for _ in range(self.height)]

        # Initialize ncurses window
        self.initialize_screen()

    def initialize_screen(self):
        # Clear the screen and setup ncurses window
        self.stdscr.clear()
        # Hide the cursor
        curses.curs_set(0)
        # Non-blocking input
        self.stdscr.nodelay(True)
        # Set getch timeout to 1ms
        self.stdscr.timeout(1)

    def clear(self):
        self.screen = [[0] * self.width for _ in range(self.height)]
        self.stdscr.clear()

    def draw_pixel(self, x, y):
        # Wrap around the screen if the coordinates are out of bounds
        x %= self.width
        y %= self.height

        # Toggle the pixel state
        self.screen[y][x] ^= 1

        # Draw the pixel to the ncurses screen
        if self.screen[y][x] == 1:
            self.stdscr.addch(y, x, "█")  # Draw a filled block
        else:
            self.stdscr.addch(y, x, " ")  # Draw an empty block

    def draw_sprite(self, x, y, sprite):
        # Draw an 8-bit sprite at the specified coordinates x,y
        collision = 0
        for byte_index in range(len(sprite)):
            sprite_byte = sprite[byte_index]
            for bit_index in range(8):
                if sprite_byte & (0x80 >> bit_index):
                    if self.screen[(y + byte_index) % self.height][(x + bit_index) % self.width] == 1:
                        collision = 1
                    self.draw_pixel(x + bit_index, y + byte_index)
        return collision

    def display_status_line(self):
        # Get the screen dimensions
        height, width = self.stdscr.getmaxyx()

        # Clear the status line before updating
        self.stdscr.move(height - 1, 0)
        self.stdscr.clrtoeol()

        # Create a single string from the status items
        status_str = " | ".join(
            f"{key}: {value}" for key, value in status_items.items())

        # Ensure the string is not longer than the screen width
        if len(status_str) > width:
            status_str = status_str[:width - 1]

        # Add the status string to the bottom of the screen
        self.stdscr.addstr(height - 1, 0, status_str, curses.A_REVERSE)

    def refresh(self):
        self.stdscr.refresh()
