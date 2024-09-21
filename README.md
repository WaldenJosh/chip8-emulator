# Chip-8 Emulator

This project is an **experimental Chip-8 emulator** written in Python, using `ncurses` for the graphical display. The emulator is a learning project and is **currently under heavy development**. Please note that **everything in this repository is subject to rapid changes**, and it is **not yet feature-complete**.

## Overview

The goal of this project is to build a fully functional Chip-8 emulator that:
- Processes all standard Chip-8 opcodes.
- Implements a basic display using `ncurses` (with plans to move to `pygame` later).
- Supports debugging and logging features to track opcode execution.

### Features (WIP)
- **Opcode Processing:** The emulator processes most basic Chip-8 opcodes, but some may still need debugging.
- **Display:** Uses `ncurses` to simulate the Chip-8's 64x32 monochrome display.
- **Debugging:** Includes an extensive logging system for tracking opcode execution and emulator state.
- **Sound & Input Handling:** Sound and input handling are planned for future implementation.

## Status

This emulator is a **work-in-progress**, and many features are incomplete or experimental. As such:
- **Do not expect full accuracy** for all opcodes at this stage.
- **Sound support is not implemented** yet.
- The **display functionality is limited** due to the current use of `ncurses`.
- **Opcode handling and other core components are still under active testing and development**.

## Setup

1. Clone the repository:

    ```bash
    git clone https://github.com/WaldenJosh/chip8-emulator.git
    ```

2. Install dependencies (none currently required besides Python 3).

3. Run the emulator with a Chip-8 ROM:

    ```bash
    python3 main.py path_to_rom.ch8
    ```

## Development Plans

- **Move to `pygame`** for improved graphical display and input handling.
- **Complete and debug all opcodes**, ensuring compatibility with multiple Chip-8 ROMs.
- **Add sound support** based on the Chip-8’s sound timer.
- **Optimize the emulator's performance** for better accuracy and efficiency.

## Contribution

Since this project is in the early stages of development, contributions are not yet being accepted. However, feedback is welcome! Feel free to open issues or submit suggestions.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Acknowledgments

- **Chip-8 Community**: For the numerous resources and tutorials on Chip-8 emulation.
- **Python and Open Source Developers**: For making tools like `ncurses` and Python possible, which power this emulator.

---

⚠️ **Disclaimer:** This project is intended for educational purposes only. It is an academic experiment and should not be considered stable or production-ready in any form.
