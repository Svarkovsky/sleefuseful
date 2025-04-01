#!/usr/bin/env python3




# MIT License
#
# Copyright (c) Ivan Svarkovsky - 2025
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.




import sys
import os
import re
from shutil import copyfile

# Версия и информация
VERSION = "0.1 (test)"
PLATFORM = "x86_64 Linux with SSE2 support"

# Справка
def show_help():
    print(f"sleefuseful - A tool to replace standard math functions with SLEEF equivalents")
    print(f"Version: {VERSION}")
    print(f"Platform: {PLATFORM}")
    print()
    print(f"Usage: {sys.argv[0]} <files> -05|-10|-35|-3500 [-sca|-vec|-auto] [-b]")
    print("Options:")
    print("  -05, -10, -35, -3500  Set precision level for SLEEF functions")
    print("  -sca                  Use scalar SLEEF functions (e.g., Sleef_sinf_u35)")
    print("  -vec                  Use vector SLEEF functions (e.g., Sleef_sinf4_u35)")
    print("  -auto                 Auto-detect scalar or vector code per line (default)")
    print("  -b                    Create backup files with .sleefuseful suffix")
    print("  -help                 Show this help message")
    print("  -version              Show version information")
    print()
    print("Example:")
    print(f"  {sys.argv[0]} *.c -35 -sca -b")
    sys.exit(0)

# Версия
def show_version():
    print(f"sleefuseful version: {VERSION}")
    print(f"Platform: {PLATFORM}")
    sys.exit(0)

# Проверка аргументов
if len(sys.argv) < 2:
    print("Error: No arguments provided")
    print(f"Use '{sys.argv[0]} -help' for usage information")
    sys.exit(1)

if sys.argv[1] == "-help":
    show_help()
elif sys.argv[1] == "-version":
    show_version()

if len(sys.argv) < 3:
    print(f"Usage: {sys.argv[0]} <files> -05|-10|-35|-3500 [-sca|-vec|-auto] [-b]")
    print(f"Use '{sys.argv[0]} -help' for more information")
    sys.exit(1)

# Определение точности
precision = sys.argv[2]
if precision not in ["-05", "-10", "-35", "-3500"]:
    print(f"Invalid precision: {precision}. Use -05, -10, -35, or -3500")
    sys.exit(1)
precision = precision.lstrip("-")
precision = f"_u{precision}"

# Определение режима
mode = "auto"
backup = False
for arg in sys.argv[3:]:
    if arg == "-sca":
        mode = "sca"
    elif arg == "-vec":
        mode = "vec"
    elif arg == "-auto":
        mode = "auto"
    elif arg == "-b":
        backup = True

# Словари замен с учетом доступных версий
scalar_replacements = {
    "sinf": f"Sleef_sinf{precision}",
    "cosf": f"Sleef_cosf{precision}",
    "tanf": f"Sleef_tanf{precision}",
    "asinf": f"Sleef_asinf{precision}",
    "acosf": f"Sleef_acosf{precision}",
    "atanf": f"Sleef_atanf{precision}",
    "atan2f": f"Sleef_atan2f{precision}",
    "sqrtf": f"Sleef_sqrtf{precision}",
    "logf": f"Sleef_logf{precision}",
    "expf": f"Sleef_expf{precision}",
    "powf": f"Sleef_powf{precision}",
    "sin": f"Sleef_sin{precision}",  # Добавлено для double
    "cos": f"Sleef_cos{precision}",  # Добавлено для double
}

vector_replacements = {
    "sinf": f"Sleef_sinf4{precision}",
    "cosf": f"Sleef_cosf4{precision}",
    "tanf": f"Sleef_tanf4{precision}",
    "asinf": f"Sleef_asinf4{precision}",
    "acosf": f"Sleef_acosf4{precision}",
    "atanf": f"Sleef_atanf4{precision}",
    "atan2f": f"Sleef_atan2f4{precision}",
    "sqrtf": f"Sleef_sqrtf4{precision}",
    "logf": f"Sleef_logf4{precision}",
    "expf": f"Sleef_expf4{precision}",
    "powf": f"Sleef_powf4{precision}",
    "sin": f"Sleef_sin2{precision}",  # Векторная версия для double (SSE2)
    "cos": f"Sleef_cos2{precision}",  # Векторная версия для double (SSE2)
}

# Корректировка для _u3500
if precision == "_u3500":
    del scalar_replacements["sqrtf"]
    del scalar_replacements["atan2f"]
    del vector_replacements["sqrtf"]
    del vector_replacements["atan2f"]
    scalar_replacements["sinf"] = "Sleef_fastsinf_u3500"
    scalar_replacements["cosf"] = "Sleef_fastcosf_u3500"
    scalar_replacements["powf"] = "Sleef_fastpowf_u3500"
    vector_replacements["sinf"] = "Sleef_fastsinf4_u3500"
    vector_replacements["cosf"] = "Sleef_fastcosf4_u3500"
    vector_replacements["powf"] = "Sleef_fastpowf4_u3500"
    scalar_replacements["sin"] = "Sleef_sin_u35"  # Откат на _u35 для double
    scalar_replacements["cos"] = "Sleef_cos_u35"  # Откат на _u35 для double
    vector_replacements["sin"] = "Sleef_sin2_u35"  # Векторная версия для double
    vector_replacements["cos"] = "Sleef_cos2_u35"  # Векторная версия для double
    for func in ["tanf", "asinf", "acosf", "atanf", "logf", "expf"]:
        scalar_replacements[func] = f"Sleef_{func}_u35"
        vector_replacements[func] = f"Sleef_{func}4_u35"
    scalar_replacements["sqrtf"] = "Sleef_sqrtf_u35"
    scalar_replacements["atan2f"] = "Sleef_atan2f_u35"
    vector_replacements["sqrtf"] = "Sleef_sqrtf4_u35"
    vector_replacements["atan2f"] = "Sleef_atan2f4_u35"

# Корректировка для _u05
if precision == "_u05":
    for func in ["tanf", "asinf", "acosf", "atanf", "atan2f", "logf", "expf", "powf", "sin", "cos"]:
        scalar_replacements[func] = f"Sleef_{func}_u10"
        vector_replacements[func] = f"Sleef_{func}4_u10" if func.endswith("f") else f"Sleef_{func}2_u10"

# Корректировка для _u10
if precision == "_u10":
    scalar_replacements["sqrtf"] = "Sleef_sqrtf_u05"
    vector_replacements["sqrtf"] = "Sleef_sqrtf4_u05"

# Корректировка для _u35
if precision == "_u35":
    scalar_replacements["powf"] = "Sleef_powf_u10"
    vector_replacements["powf"] = "Sleef_powf4_u10"

# Счетчики
counts_scalar = {func: 0 for func in scalar_replacements}
counts_vector = {func: 0 for func in vector_replacements}

# Обработка файлов
for file in sys.argv[1:]:
    if file.startswith("-") or not file.endswith(".c"):
        continue

    print(f"Processing {file}...")

    # Чтение файла
    with open(file, "r") as f:
        lines = f.readlines()

    # Проверка заголовков и векторного кода
    has_sleef = any("#include <sleef.h>" in line for line in lines)
    has_emmintrin = any("#include <emmintrin.h>" in line for line in lines)
    has_math = any("#include <math.h>" in line for line in lines)
    is_vector = any(re.search(r"__m128|_mm_", line) for line in lines)
    new_lines = lines[:]

    # Добавление или замена заголовков
    if has_math and not has_sleef:
        math_idx = next((i for i, line in enumerate(lines) if "#include <math.h>" in line), -1)
        if math_idx != -1:
            new_lines[math_idx] = "#include <sleef.h>\n"
            print(f"Replaced #include <math.h> with #include <sleef.h> in {file}")
        else:
            include_idx = next((i for i, line in enumerate(lines) if line.startswith("#include")), 0)
            new_lines.insert(include_idx, "#include <sleef.h>\n")
            print(f"Added #include <sleef.h> to {file}")
    elif not has_sleef:
        include_idx = next((i for i, line in enumerate(lines) if line.startswith("#include")), 0)
        new_lines.insert(include_idx, "#include <sleef.h>\n")
        print(f"Added #include <sleef.h> to {file}")

    if mode == "vec" or (mode == "auto" and is_vector):
        if not has_emmintrin:
            sleef_idx = next((i for i, line in enumerate(new_lines) if "#include <sleef.h>" in line), 0)
            new_lines.insert(sleef_idx + 1, "#include <emmintrin.h>\n")
            print(f"Added #include <emmintrin.h> to {file} for SSE2 support")

    # Построчная обработка
    for i, line in enumerate(new_lines):
        new_line = line
        for func in scalar_replacements:
            if re.search(r"\b" + func + r"\b", line):
                if mode == "sca" or (mode == "auto" and not re.search(r"__m128|_mm_", line)):
                    new_line = re.sub(r"\b" + func + r"\b", scalar_replacements[func], new_line)
                    counts_scalar[func] += len(re.findall(r"\b" + func + r"\b", line))
                elif mode == "vec" or (mode == "auto" and re.search(r"__m128|_mm_", line)):
                    new_line = re.sub(r"\b" + func + r"\b", vector_replacements[func], new_line)
                    counts_vector[func] += len(re.findall(r"\b" + func + r"\b", line))
        new_lines[i] = new_line

    # Создание бэкапа
    if backup:
        backup_file = f"{file}.sleefuseful"
        copyfile(file, backup_file)
        print(f"Backup created: {backup_file}")

    # Запись изменений
    with open(file, "w") as f:
        f.writelines(new_lines)

    # Вывод статистики
    print(f"\nReplacements in {file} with precision {precision} ({mode}):")
    total = 0
    if mode == "sca" or mode == "auto":
        for func, count in counts_scalar.items():
            if count > 0:
                print(f"{func} -> {scalar_replacements[func]}: {count}")
                total += count
    if mode == "vec" or mode == "auto":
        for func, count in counts_vector.items():
            if count > 0:
                print(f"{func} -> {vector_replacements[func]}: {count}")
                total += count
    print(f"Total replacements in {file}: {total}")

sys.exit(0)
