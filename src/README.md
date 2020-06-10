# Castoro sources

The glyph design sources are in FontLab 7 .vfc format. These sources also contain the classes and kerning data used in the OpenType Layout GPOS table, but not the GSUB groups and lookups.

The OpenType Layout sources are in Microsoft‘s Visual OpenType Layout Tool .vtp format. This is a plain text format that can be imported into a TrueType font and edited in [MS VOLT](https://docs.microsoft.com/en-us/typography/tools/volt/). If desired, the .vtp OTL sources can be converted to the more common AFDKO .fea format using our [Volto](https://github.com/TiroTypeworks/Volto) conversion tool.

TrueType hinting sources are available as Microsoft Visual TrueType ([VTT](https://docs.microsoft.com/en-us/typography/tools/vtt/)) private tables in TTF files. These are currently autohinted in VTT and not additional manual hinting has been done.