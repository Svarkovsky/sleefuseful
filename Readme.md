```markdown
# sleefuseful

A Python tool to automate replacing standard `math.h` functions with their high-performance SLEEF (SIMD Library for Evaluating Elementary Functions) equivalents in C code.

## Description

`sleefuseful` simplifies the process of optimizing C code by automatically substituting standard math functions (like `sinf`, `cosf`, `sqrtf`) with faster, vectorized versions from the SLEEF library. It processes specified C files, modifies the source code to use SLEEF functions, and provides options for precision levels, scalar/vector function selection, and creating backup files.

## Features

*   **Automated SLEEF Integration:**  Replaces standard math functions with SLEEF equivalents.
*   **Precision Control:** Select from different precision levels for SLEEF functions (`-05`, `-10`, `-35`, `-3500`).
*   **Scalar/Vector Selection:** Choose between scalar (`-sca`) and vector (`-vec`) versions of SLEEF functions, or let the script automatically detect the appropriate version (`-auto`).
*   **Backup Support:** Creates backup copies of modified files before making changes (`-b`).
*   **Clear Statistics:**  Provides a summary of replacements made in each file.

## Requirements

*   Python 3.x
*   SLEEF library (must be downloaded and built separately - see instructions below)
*   `sed`, `grep`, `cp` commands (typically available on Linux/macOS)

## Installation

1.  **Install Python 3:** Make sure you have Python 3 installed on your system.
2.  **Download SLEEF:** Download the SLEEF library from [https://sleef.org/](https://sleef.org/) or its GitHub repository: [https://github.com/sleef/sleef](https://github.com/sleef/sleef).
3.  **Build SLEEF:** Follow the SLEEF build instructions. Common command for building SLEEF are:
    ```bash
    mkdir build
    cd build
    cmake ..
    make
    sudo make install # (or local make install to a folder for local usage)
    ```
4.  **Copy `sleefuseful.py` to your project directory:** Place the `sleefuseful.py` script in the same directory as your C source files.

## Usage

```bash
./sleefuseful.py <files> -<precision> [-sca|-vec|-auto] [-b]
```

*   `<files>`:  One or more C source files to process (e.g., `*.c`, `file1.c file2.c`).
*   `-<precision>`:  Required.  Specifies the precision level for SLEEF functions. Choose one of:
    *   `-05`: Fastest, least accurate.
    *   `-10`:
    *   `-35`:  Good balance between speed and accuracy (recommended).
    *   `-3500`: Highest accuracy, potentially slower.

*   `[-sca|-vec|-auto]`:  Optional.  Specifies the type of SLEEF functions to use:
    *   `-sca`: Use scalar SLEEF functions (e.g., `Sleef_sinf_u35`).
    *   `-vec`: Use vector SLEEF functions (e.g., `Sleef_sinf4_u35`) - **requires SSE2 support**.
    *   `-auto`:  (Default). Automatically detect scalar or vector code based on the presence of SSE intrinsics (`__m128`, `_mm_`) in each line.
*   `[-b]`: Optional. Create backup files with a `.sleefuseful` suffix before modifying the originals.

**Examples:**

```bash
./sleefuseful.py *.c -35 -sca -b
```

Replaces math functions in all `.c` files in the current directory with scalar SLEEF functions at `_u35` precision, creating backup files.

```bash
./sleefuseful.py my_file.c -10 -vec
```

Replaces math functions in `my_file.c` with vector SLEEF functions at `_u10` precision (no backup).

## Notes

*   **Dependencies:** Make sure you have `sed`, `grep`, and `cp` installed on your system. These are standard utilities on most Linux/macOS systems.
*   **Backup:** It is highly recommended to use the `-b` option to create backups of your files before running the script.
*   **SSE2:** Vectorization (`-vec` or `-auto` with vector code) requires a processor with SSE2 support and proper SSE2 compilation flags (e.g., `-msse2` in GCC).
*   **SLEEF Installation:** This tool assumes that you have already downloaded and built the SLEEF library.
*   **Testing:** Always test your code thoroughly after using `sleefuseful` to ensure that the changes are correct and do not introduce any new issues.

## License

This script is released under the MIT License.

Copyright (c) 2025 Ivan Svarkovsky - [https://github.com/Svarkovsky](https://github.com/Svarkovsky)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
