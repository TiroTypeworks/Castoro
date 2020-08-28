# Castoro sources

The glyph design sources are in FontLab 7 .vfj format. These sources also contain the classes and kerning data used in the OpenType Layout GPOS table, and the GSUB code in .fea format.

The OpenType Layout for the Castoro fonts was initially developed in Microsoft‘s Visual OpenType Layout Tool .vtp format, then converted to .fea syntax using our [Volto](https://github.com/TiroTypeworks/Volto) conversion tool, and integrated into the FontLab 7 .vfj sources. As of version 1.10 (build 002), the .vfj files should be considered the source for OTL, and the previously available .vtp files have been removed from the repo.

## Building the Fonts

Family is built using fontmake and gftools post processing script. Tools are all python based.

To install all the Python tools into a virtualenv, do the following:

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Then run the build script in the terminal:

```
cd sources
sh build.sh
```
