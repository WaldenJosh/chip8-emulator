# cpu.py

import random
from py import std
from globals import status_items
from globals import log_debug
from display import Display

# Memory constants
MEMORY_SIZE = 4096  # Total size for Chip-8 memory
FONT_START = 0x050  # Start of fontset in memory
PROGRAM_START_ADDRESS = 0x200  # Start of program memory

# Fontset for the Chip-8 (Each charachter is 4x5 pixels)
FONT_SET = [
    0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
    0x20, 0x60, 0x20, 0x20, 0x70,  # 1
    0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
    0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
    0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
    0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
    0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
    0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
    0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
    0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
    0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
    0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
    0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
    0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
    0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
    0xF0, 0x80, 0xF0, 0x80, 0x80   # F
]


# Chip-8 CPU class
class CPU:
    def __init__(self, stdscr):
        # Initialize the Display
        self.display = Display(stdscr)

        # Initialize the registers and memory pointers
        self.v = [0] * 16  # 16 8-bit registers V0 - VF
        self.i = 0  # Index register
        self.pc = PROGRAM_START_ADDRESS  # Program counter
        self.stack = []  # Stack
        self.sp = 0  # Stack pointer
        self.delay_timer = 0
        self.sound_timer = 0
        self.keys = [0] * 16  # Key states for Chip-8 keys

        # Initialize the memory
        self.memory = bytearray([0] * MEMORY_SIZE)
        self.initialize_memory()

    # Function to read memory
    def read_memory(self, address, length=1):
        return self.memory[address:address + length]

    # Function to write to memory
    def write_memory(self, address, data):
        for i in range(len(data)):
            self.memory[address + i] = data[i]

    # Initialize the memory, clear and load the fontset

    def initialize_memory(self):
        # Clear the memory
        for i in range(MEMORY_SIZE):
            self.memory[i] = 0

        # Load the fontset into memory
        for i in range(len(FONT_SET)):
            self.memory[FONT_START + i] = FONT_SET[i]

    # Function to load a program into memory

    def load_rom(self, rom_path):
        with open(rom_path, "rb") as rom_file:
            rom_data = rom_file.read()
            for i in range(len(rom_data)):
                self.memory[PROGRAM_START_ADDRESS + i] = rom_data[i]

        # Update the status dictionary item 'rom' with the ROM filename
        status_items["rom"] = f"{rom_path.split('/')[-1]} loaded"

    # Function to fetch the next opcode (2 bytes) from memory
    def fetch_opcode(self):
        opcode = self.memory[self.pc] << 8 | self.memory[self.pc + 1]
        return opcode

    # Function to decode and execute an opcode
    def execute_opcode(self, opcode):
        # Program counter flag to indicate if it has changed
        pc_changed = False

        # Update the status dictionary item 'opcode' with the current opcode
        # Format the opcode as a 4-digit hexadecimal number
        status_items["opcode"] = f"{opcode:04X}"

        # Decode and execute the opcode
        first_nibble = opcode & 0xF000

        log_debug(f"Executing opcode: {opcode:04X}")

        if first_nibble == 0x0000:
            if opcode == 0x00E0:
                log_debug(f"Opcode 00E0: Clear the screen")
                self.clear_screen()
            elif opcode == 0x00EE:
                log_debug(f"Opcode 00EE: Return from subroutine")
                self.return_from_subroutine()
            else:
                self.unknown_opcode(opcode)

        elif first_nibble == 0x1000:  # 1NNN: Jump to address NNN
            address = opcode & 0x0FFF
            log_debug(f"Opcode 1NNN: Jump to address {address:04X}")
            self.pc = address
            pc_changed = True

        elif first_nibble == 0x2000:  # 2NNN: Call subroutine at NNN
            address = opcode & 0x0FFF
            log_debug(f"Opcode 2NNN: Call subroutine at {address:04X}")
            self.stack.append(self.pc)
            self.sp += 1
            self.pc = address
            pc_changed = True

        elif first_nibble == 0x3000:  # 3XKK: Skip next instruction if Vx == kk
            x = (opcode & 0x0F00) >> 8
            kk = opcode & 0x00FF
            log_debug(f"Opcode 3Xnn: Checking V{x} = {self.v[x]:02X} against kk = {kk:02X}")
            if self.v[x] == kk:
                self.pc += 2
                pc_changed = True
                log_debug(f"Opcode 3Xnn: Skipping next instruction, PC = {self.pc:04X}")

        elif first_nibble == 0x4000:  # 4XKK: Skip next instruction if Vx != kk
            x = (opcode & 0x0F00) >> 8
            kk = opcode & 0x00FF
            log_debug(f"Opcode 4Xnn: Checking V{x} != {kk:02X}")
            if self.v[x] != kk:
                self.pc += 2
                pc_changed = True

        elif first_nibble == 0x5000:  # 5XY0: Skip next instruction if Vx == Vy
            x = (opcode & 0x0F00) >> 8
            y = (opcode & 0x00F0) >> 4
            log_debug(f"Opcode 5XY0: Checking V{x} == V{y}")
            if self.v[x] == self.v[y]:
                self.pc += 2
                pc_changed = True

        elif first_nibble == 0x6000:  # 6XKK: Set Vx = kk
            x = (opcode & 0x0F00) >> 8
            kk = opcode & 0x00FF
            log_debug(f"Opcode 6XKK: Setting V{x} = {kk:02X}")
            self.v[x] = kk

        elif first_nibble == 0x7000:  # 7XKK: Set Vx = Vx + kk
            x = (opcode & 0x0F00) >> 8
            kk = opcode & 0x00FF
            log_debug(f"Opcode 7XKK: Adding kk = {kk:02X} to V{x} = {self.v[x]:02X}")
            self.v[x] = (self.v[x] + kk) & 0xFF

        elif first_nibble == 0x8000:
            x = (opcode & 0x0F00) >> 8
            y = (opcode & 0x00F0) >> 4
            last_nibble = opcode & 0x000F

            if last_nibble == 0x0:  # 8XY0: Set Vx = Vy
                log_debug(f"Opcode 8XY0: Setting V{x} = V{y}")
                self.v[x] = self.v[y]
            elif last_nibble == 0x1:  # 8XY1: Set Vx = Vx OR Vy
                log_debug(f"Opcode 8XY1: Setting V{x} = V{x} | V{y}")
                self.v[x] |= self.v[y]
            elif last_nibble == 0x2:  # 8XY2: Set Vx = Vx AND Vy
                log_debug(f"Opcode 8XY2: Setting V{x} = V{x} & V{y}")
                self.v[x] &= self.v[y]
            elif last_nibble == 0x3:  # 8XY3: Set Vx = Vx XOR Vy
                log_debug(f"Opcode 8XY3: Setting V{x} = V{x} ^ V{y}")
                self.v[x] ^= self.v[y]
            elif last_nibble == 0x4:  # 8XY4: Set Vx = Vx + Vy, set VF = carry
                result = self.v[x] + self.v[y]
                log_debug(f"Opcode 8XY4: Adding V{y} = {self.v[y]:02X} to V{x} = {self.v[x]:02X}, setting VF = {1 if result > 0xFF else 0}")
                self.v[0xF] = 1 if result > 0xFF else 0
                self.v[x] = result & 0xFF
            elif last_nibble == 0x5:  # 8XY5: Set Vx = Vx - Vy, set VF = NOT borrow
                result = self.v[x] - self.v[y]
                log_debug(f"Opcode 8XY5: Subtracting V{y} from V{x}, setting VF = {1 if self.v[x] >= self.v[y] else 0}")
                self.v[0xF] = 1 if self.v[x] >= self.v[y] else 0
                self.v[x] = result & 0xFF
            elif last_nibble == 0x6:  # 8XY6: Set Vx = Vx SHR 1
                log_debug(f"Opcode 8XY6: Shifting V{x} right by 1, setting VF = {self.v[x] & 0x1}")
                self.v[0xF] = self.v[x] & 0x1
                self.v[x] >>= 1
            elif last_nibble == 0x7:  # 8XY7: Set Vx = Vy - Vx, set VF = NOT borrow
                result = self.v[y] - self.v[x]
                log_debug(f"Opcode 8XY7: Subtracting V{x} from V{y}, setting VF = {1 if self.v[y] >= self.v[x] else 0}")
                self.v[0xF] = 1 if self.v[y] >= self.v[x] else 0
                self.v[x] = result & 0xFF
            elif last_nibble == 0xE:  # 8XYE: Set Vx = Vx SHL 1
                log_debug(f"Opcode 8XYE: Shifting V{x} left by 1, setting VF = {(self.v[x] & 0x80) >> 7}")
                self.v[0xF] = (self.v[x] & 0x80) >> 7
                self.v[x] = (self.v[x] << 1) & 0xFF
            else:
                self.unknown_opcode(opcode)

        elif first_nibble == 0x9000:  # 9XY0: Skip next instruction if Vx != Vy
            x = (opcode & 0x0F00) >> 8
            y = (opcode & 0x00F0) >> 4
            log_debug(f"Opcode 9XY0: Checking V{x} != V{y}")
            if self.v[x] != self.v[y]:
                self.pc += 2
                pc_changed = True

        elif first_nibble == 0xA000:  # ANNN: Set I = NNN
            self.i = opcode & 0x0FFF
            log_debug(f"Opcode ANNN: Setting I = {self.i:04X}")

        elif first_nibble == 0xB000:  # BNNN: Jump to address NNN + V0
            self.pc = (opcode & 0x0FFF) + self.v[0]
            pc_changed = True
            log_debug(f"Opcode BNNN: Jumping to address {self.pc:04X} (NNN + V0)")

        elif first_nibble == 0xC000:  # CXKK: Set Vx = random byte AND kk
            x = (opcode & 0x0F00) >> 8
            kk = opcode & 0x00FF
            random_value = random.randint(0, 255)
            self.v[x] = random_value & kk
            log_debug(f"Opcode CXKK: Setting V{x} to random byte AND {kk:02X}, value = {self.v[x]:02X}")

        elif first_nibble == 0xD000:  # DXYN: Display n-byte sprite at (Vx, Vy)
            x = (opcode & 0x0F00) >> 8
            y = (opcode & 0x00F0) >> 4
            n = opcode & 0x000F
            log_debug(f"Opcode DXYN: Drawing sprite at (V{x}, V{y}) with height {n}")
            self.draw_sprite(self.v[x], self.v[y], n)

        elif first_nibble == 0xE000:
            x = (opcode & 0x0F00) >> 8
            if (opcode & 0x00FF) == 0x9E:  # EX9E: Skip next instruction if key with the value of Vx is pressed
                log_debug(f"Opcode EX9E: Skipping if key in V{x} is pressed")
                pass  # TODO: Implement key handling
            elif (opcode & 0x00FF) == 0xA1:  # EXA1: Skip next instruction if key with the value of Vx is not pressed
                log_debug(f"Opcode EXA1: Skipping if key in V{x} is not pressed")
                pass  # TODO: Implement key handling
            else:
                self.unknown_opcode(opcode)

        elif first_nibble == 0xF000:
            x = (opcode & 0x0F00) >> 8
            last_byte = opcode & 0x00FF

            if last_byte == 0x07:  # FX07: Set Vx = delay timer value
                log_debug(f"Opcode FX07: Setting V{x} = delay timer ({self.delay_timer})")
                self.v[x] = self.delay_timer
            elif last_byte == 0x0A:  # FX0A: Wait for a key press, store the value of the key in Vx
                log_debug(f"Opcode FX0A: Waiting for a key press")
                self.v[x] = self.wait_for_key_press()
            elif last_byte == 0x15:  # FX15: Set delay timer = Vx
                log_debug(f"Opcode FX15: Setting delay timer = V{x} ({self.v[x]:02X})")
                self.delay_timer = self.v[x]
            elif last_byte == 0x18:  # FX18: Set sound timer = Vx
                log_debug(f"Opcode FX18: Setting sound timer = V{x} ({self.v[x]:02X})")
                self.sound_timer = self.v[x]
            elif last_byte == 0x1E:  # FX1E: Set I = I + Vx
                log_debug(f"Opcode FX1E: Adding V{x} = {self.v[x]:02X} to I = {self.i:04X}")
                self.i = (self.i + self.v[x]) & 0xFFFF
            elif last_byte == 0x29:  # FX29: Set I = location of sprite for digit Vx
                log_debug(f"Opcode FX29: Setting I = location of sprite for digit V{x}")
                self.i = FONT_START + (self.v[x] * 5)
            elif last_byte == 0x33:  # FX33: Store BCD representation of Vx in memory locations I, I+1, and I+2
                log_debug(f"Opcode FX33: Storing BCD of V{x} = {self.v[x]:02X} at memory location I")
                self.memory[self.i] = self.v[x] // 100
                self.memory[self.i + 1] = (self.v[x] // 10) % 10
                self.memory[self.i + 2] = (self.v[x] % 10)
            elif last_byte == 0x55:  # FX55: Store registers V0 through Vx in memory starting at location I
                log_debug(f"Opcode FX55: Storing registers V0 through V{x} starting at I = {self.i:04X}")
                for register_index in range(x + 1):
                    self.memory[self.i + register_index] = self.v[register_index]
            elif last_byte == 0x65:  # FX65: Read registers V0 through Vx from memory starting at location I
                log_debug(f"Opcode FX65: Reading registers V0 through V{x} from I = {self.i:04X}")
                for register_index in range(x + 1):
                    self.v[register_index] = self.memory[self.i + register_index]
            else:
                self.unknown_opcode(opcode)

        else:
            self.unknown_opcode(opcode)

        if not pc_changed:  # If the program counter has not been changed
            self.pc += 2

        log_debug(f"PC after opcode execution: {self.pc:04X}")

    def wait_for_key_press(self):
        # Loop until a key is pressed
        while True:
            key = self.display.stdscr.getch()  # Get a key press from ncurses
            if key != -1:  # A key was pressed
                chip8_key = self.map_key_to_chip8(key)
                if chip8_key != -1:  # Ensure the key is mapped
                    return chip8_key
                
    def is_key_pressed(self, key_value):
        return self.keys[key_value] == 1  # Return True if the key is pressed

    def map_key_to_chip8(self, key):
        # Example key mapping (adjust according to your specific setup)
        key_map = {
            ord('1'): 0x1, ord('2'): 0x2, ord('3'): 0x3, ord('4'): 0xC,
            ord('q'): 0x4, ord('w'): 0x5, ord('e'): 0x6, ord('r'): 0xD,
            ord('a'): 0x7, ord('s'): 0x8, ord('d'): 0x9, ord('f'): 0xE,
            ord('z'): 0xA, ord('x'): 0x0, ord('c'): 0xB, ord('v'): 0xF,
        }
        return key_map.get(key, -1)  # Return -1 if the key is not mapped

    # Function to clear the screen
    def clear_screen(self):
        self.display.clear()

    # Function to handle drawing sprites
    def draw_sprite(self, x, y, n):
        # Get the sprite data from memory (n bytes starting at I)
        sprite = self.memory[self.i:self.i + n]  # n determines the height
        collision = self.display.draw_sprite(x, y, sprite)

        # Set VF register to 1 if a collision occurred
        self.v[0xF] = collision

    # Function to return from a subroutine
    def return_from_subroutine(self):
        self.pc = self.stack.pop()

    # Function to update error in the status dictionary if we encounter an unknown opcode
    def unknown_opcode(self, opcode):
        status_items["error"] = f"Unknown opcode: {opcode:X}"

    # Main loop to fetch, decode, and execute instructions
    def run(self):
        opcode = self.fetch_opcode()
        self.execute_opcode(opcode)

        # Handle timers
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1
