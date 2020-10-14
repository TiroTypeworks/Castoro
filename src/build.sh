#!/bin/sh
set -e

mkdir -p ../fonts/otf ../fonts/ttf

echo = "Generating TTFs"
fontmake -u ./UFO/Castoro-Regular.ufo -o ttf --output-dir ../fonts/ttf -a
fontmake -u ./UFO/Castoro-Italic.ufo -o ttf --output-dir ../fonts/ttf -a
# fontmake -m ./UFO/Castoro_Roman.designspace -o ttf --output-dir ../fonts/ttf -a
# fontmake -m ./UFO/Castoro_Italic.designspace -o ttf --output-dir ../fonts/ttf -a

echo = "Post procesing TTF"
ttfs=$(ls ../fonts/ttf/*.ttf)
for ttf in $ttfs
do
    gftools fix-hinting $ttf
    mv "$ttf.fix" $ttf
    gftools fix-dsig -f $ttf;
    python3 castoro_stat_table.py $ttfs
done

echo = "Generating OTFs"
fontmake -u ./UFO/Castoro-Regular.ufo -o otf --output-dir ../fonts/otf
fontmake -u ./UFO/Castoro-Italic.ufo -o otf --output-dir ../fonts/otf
# fontmake -m ./UFO/Castoro_Roman.designspace -o otf --output-dir ../fonts/otf
# fontmake -m ./UFO/Castoro_Italic.designspace -o otf --output-dir ../fonts/otf

echo "Post processing static OTFs"
otf=$(ls ../fonts/otf/*.otf)
for otf in $otf
do
	gftools fix-dsig -f $otf;
    psautohint $otf;
done

echo "Done!"