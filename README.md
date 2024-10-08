![Castoro banner](https://github.com/TiroTypeworks/Castoro/blob/master/CastoroBanner.png)

**Castoro** is a libre font family released under the SIL Open Font License. Castoro is a specific instance of an adaptive design developed for Tiro Typeworks’ internal use as a base from which to generate tailored Latin companions for some of our non-European script types. The instance that has been expanded to create the Castoro fonts was initially made for the Indic fonts that we produced for Harvard University Press. In the Castoro version, we have retained the extensive diacritic set for transliteration of South Asian languages, and added additional characters for an increased number of European languages.
The parent design here presented as the Castoro instance began as a synthesis of aspects of assorted Dutch types from the 16–18th Centuries. Castoro roman was designed by John Hudson, and the italic with his Tiro colleague Paul Hanslow, assisted by [Kaja Słojewska](https://nomadfonts.com/). The extended Castoro collection consists of Castoro regular and italic text fonts, published in June 2020, and the all-caps Castoro Titling font, published in December 2020.
Why ‘Castoro’? One wants a typeface name to be easy to remember, and to be evocative of some association or characteristic of the design—poetic even. For our libre and open source projects, we have added the restrictive convention that the name must end in the letter –o. Castoro is named for the North American beaver, *Castor canadensis.* Robust serif text types with extensive language and typographic layout support are sometimes referred to as ‘workhorse’ types. Castoro may be thought of as a busy beaver.
The splendid beaver illustration that adorns this page and other Castoro materials is by [Lucy Conklin](http://www.lucyconklin.com/), and is used with permission.

### Version 3.01, October 2024

Version 3.01 of the Castoro text fonts includes new medium, semibold, and bold weights, totalling eight fonts in roman and italic styles. These new weights are instantiated from a variable font design space defined by regular and bold weight masters. The build process will first build the variable font and then output the static instances. Various small changes have been made to prior outlines and some revisions to spacing and kerning for consistency across the weight range.

*Note that the variable and static fonts have compatible naming, and the locations of the static fonts in the variable design space are named instances. You should install either the variable or static fonts, not both.*

Version 3.01 of the Castoro Titling font has been *thoroughly* respaced and fixes made to some kerning for overall improved evenness of setting. The spacing is slightly tighter than previously.

**Important:** Spacing and kerning revisions in this version constitute a ‘breaking change’ that will cause text to reflow when the font is updated. If you need to preserve text layout consistency in existing documents made with the previous version, download the [Castoro 2.04 release.](https://github.com/TiroTypeworks/Castoro/releases/tag/v2.04)

### Sources

The canonical design sources for the Castoro project are the FontLab 8 `.vfj` files in the source folder. These sources contain all necessary aspects of the Castoro typefaces, including the OpenType Layout coding and kerning.

The `.ufo` build input sources are exported from FontLab 8 using the default UFO package profile.

The new v3.01 variable font build and derived static fonts require the UFO files and accompanying designspace files.### Build process

The Castoro fonts use a build process based on the one that Tiro Typeworks also uses for its commercial library and client projects. The `tirobuild.py` script uses a YAML configuration file to identify UFO build sources and version string (the YAML file may contain additional, optional parameters that are not used in the Castoro project).

The build script outputs TTF and CFF OpenType fonts, and WOFF and WOFF2 packaging of each (this is hard coded and not configurable). The sequence of operations is:

* build TTF/OTF
* remove overlaps
* autohint (ttfautohint and AFDKO)
* optimise
* build WOFF/WOFF2

### Usage

From the top level, Castoro folder:

```
# Create a new virtualenv
python3 -m venv venv
# Activate env
source venv/bin/activate
# Install dependencies
pip3 install -r requirements.txt
```

For subsequent use (presuming the requirements have not changed), only the second of those steps will be required.

Run the build script indicating the YAML configuration file (for separate text and titling font build streams, use the separate YAML files).

`$ python tools/tirobuild.py castoro-all.yml`




