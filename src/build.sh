#!/bin/sh
set -e

mkdir -p ../fonts/otf ../fonts/ttf

echo = "Generating TTFs"
../venv/bin/fontmake -u ./UFO/Castoro-Regular.ufo -o ttf --output-dir ../fonts/ttf -a
../venv/bin/fontmake -u ./UFO/Castoro-Italic.ufo -o ttf --output-dir ../fonts/ttf -a

echo = "Post procesing TTF"
ttfs=$(ls ../fonts/ttf/*.ttf)
for ttf in $ttfs
do
    python ../venv/bin/gftools fix-hinting $ttf
    mv "$ttf.fix" $ttf
    python ../venv/bin/gftools fix-dsig -f $ttf;
done

echo = "Generating OTFs"
../venv/bin/fontmake -u ./UFO/Castoro-Regular.ufo -o otf --output-dir ../fonts/otf
../venv/bin/fontmake -u ./UFO/Castoro-Italic.ufo -o otf --output-dir ../fonts/otf

echo "Post processing static OTFs"
otf=$(ls ../fonts/otf/*.otf)
for otf in $otf
do
	python ../venv/bin/gftools fix-dsig -f $otf;
    ../venv/bin/psautohint $otf;
done

echo "Done!"