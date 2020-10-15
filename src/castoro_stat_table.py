#!/usr/bin/env python3
# Copyright 2020 Google LLC

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from fontTools.otlLib.builder import buildStatTable
from fontTools.ttLib import TTFont

UPRIGHT_AXES = [
    dict(
        tag="wght",
        name="Weight",
        ordering=0,
        values=[
            dict(value=400, name="Regular", flags=0x2, linkedValue=1)  # Regular
        ],    
    ),
    dict(
        tag="ital",
        name="Italic",
        ordering=1,
        values=[
            dict(value=0, name="Regular", flags=0x2)  # Regular
        ],
    ),
]

ITALIC_AXES = [
    dict(
        tag="wght",
        name="Weight",
        ordering=0,
        values=[
            dict(value=400, name="Regular", flags=0x2)  # Regular
        ],
    ),
    dict(
        tag="ital",
        name="Italic",
        ordering=1,
        values=[
            dict(value=1, name="Italic") # Italic
        ],
    ),
]

STATIC_DIR = "../fonts/ttf"
CAS_UPRIGHT = f"{STATIC_DIR}/Castoro-Regular.ttf"
CAS_ITALIC = f"{STATIC_DIR}/Castoro-Italic.ttf"


def main():
    # process upright files
    filepath = CAS_UPRIGHT
    tt = TTFont(filepath)
    buildStatTable(tt, UPRIGHT_AXES)
    tt.save(filepath)
    print(f"[STAT TABLE] Added STAT table to {filepath}")

    # process italics files
    filepath = CAS_ITALIC
    tt = TTFont(filepath)
    buildStatTable(tt, ITALIC_AXES)
    tt.save(filepath)
    print(f"[STAT TABLE] Added STAT table to {filepath}")


if __name__ == "__main__":
    main()
