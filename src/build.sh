#!/bin/sh
set -e

mkdir -p ../fonts/otf ../fonts/ttf

echo = "Generating TTFs"
fontmake -m ./UFO/Castoro_Roman.designspace -o ttf --output-dir ../fonts/ttf -a
fontmake -m ./UFO/Castoro_Italic.designspace -o ttf --output-dir ../fonts/ttf -a

echo = "Post procesing TTF"
ttfs=$(ls ../fonts/ttf/*.ttf)
for ttf in $ttfs
do
    gftools fix-dsig -f $ttf;
    gftools fix-hinting $ttf
    mv "$ttf.fix" $ttf
done

echo "Done!"