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

echo = "Generating OTFs"
fontmake -m ./UFO/Castoro_Roman.designspace -o otf --output-dir ../fonts/otf -a
fontmake -m ./UFO/Castoro_Italic.designspace -o otf --output-dir ../fonts/otf -a

echo "Post processing static OTFs"
otf=$(ls ../fonts/otf/*.otf)
for otf in $otf
do
	gftools fix-dsig -f $otf
done

echo "Done!"