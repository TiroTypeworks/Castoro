# Tiro Builder

A build tool that is configurable using a YAML text file, and is adaptable to a number of different ways in which Tiro projects are developed. The core input sources are UFO files, but the build can be configured to import specific tables from TTF sources (useful for projects that use VOLT for OpenType Layout development), apply glyph renaming using a .ren mapping file, produce subset fonts based on .txt glyph lists (using output names from .ren), and can touch up name table and embedding bit content e.g. for different licensing streams.

The build script outputs both static and variable TTF and CFF OpenType fonts, and WOFF and WOFF2 packaging of each. The sequence of operations is:

* [set final glyph names from .ren mapping]
* build TTF/OTF
* – build variable font
* [– instantiate instances]
* [remove overlaps]
* [copy OTL tables from input.ttf sources]
* autohint (ttfautohint and AFDKO)
* [subset
* – optimise subset
* – build WOFF/WOFF2 of subsets]
* optimise
* build WOFF/WOFF2

## Usage

From the top level folder:

```
# Create a new virtualenv
python3 -m venv venv

# Activate env
source venv/bin/activate

# Install dependencies
pip3 install -r requirements.txt
```

For subsequent use (presuming the requirements have not changed), only the second of those steps will be required.

Run the build script indicating a YAML configuration file (for separate build streams, use separate YAML files).

```
$ python Builder/tirobuild.py path-to-configuration.yml
```

## Sample YAML format

The format of the YAML file looks like this:

```yaml
[Optional top level keys, e.g. names, meta, instaces]

fonts:
  Foo-Regular:
    source: source/Foo-Regular.ufo
    [Optional font level keys, e.g. subsets, glyphnames, ttf]

  Foo-Bold:
    source: source/Foo-Bold.ufo
    ...
```

The only required top level key is `fonts` which is a list of static or variable fonts to build. Other top level keys are optional and when present will apply to all fonts unless overridden by per-font keys.

The only required entry for each font is the `source` input file. Other keys are optional, and when present they apply to the current font and override the respective top level keys.

Here is an example of a richly keyed configuration file to build a variable font from a designspace file + UFOs, generate static fonts from named instances, affect some special name and OS/2 table entries, generate a meta table, grab OpenType Layout tables from compiled TTFs, etc.

```yaml
names:
  5: Version 1.23
  13: This font is licensed for the exclusive use of Acme Corp and its subsidiaries.

set:
  fstype: [3]

meta:
  slng: [Adlm, Latn]
  dlng: [Adlm]

instances: all

fonts:
  Foo-Roman:
    source: source/Foo-Roman.designspace
    subsets:
      Foo-Roman:
        glyphlist: source/FooAdlamSubset.txt
        names:
          1: Foo Adlam
          4: Foo Adlam
          6: FooAdlam-Regular
    glyphnames: source/Foo.ren
    ...
```
Here is an snippet of example configuration for explicit static instance generation from a variable build:

```yaml
instances:
  Foo-Regular:
    coordinates:
      wght: 320
    names:
      1: Foo
      2: Regular
      4: Foo
      6: Brill-Regular
  Foo-Medium
    coordinates:
      wght: 360
    names:
      1: Foo Medium
      2: Regular
      4: Foo Medium
      6: FooMedium-Regular
      16: Foo
      17: Medium
```

## All supported keys follow:

`fonts:` a dictionary of fonts to be built, the key of each entry will be used a the stem of the filename of the generated fonts:

```yaml
fonts:
  Brill-Regular:
    source: source/Brill-Regular.ufo

  Brill-Bold:
    source: source/Brill-Bold.ufo
```

This will create `Brill-Regular.ttf`, `Brill-Bold.ttf`, `Brill-Regular.otf`, `Brill-Bold.otf`, and so on.

---

`source:` the input font file, it can either be a `.ufo` for static fonts or `.designspace` for variable fonts.

```yaml
fonts:
  Brill-Roman:
    source: source/Brill-Roman.designspace

  Brill-Regular:
    source: source/Brill-Regular.ufo
```

---

`ttf:` copy compiled font tables from a binary font. Has to sub-keys; `source:` the input binary font path, and `tables:` a list of table tags to copy:

```yaml
ttf:
  source: source/Brill-Italic.input.ttf
  tables: [GDEF, GSUB, GPOS]
```

For variable fonts, `source` must be a list of files, each corresponding to a DesignSpace master and in the same order:

```yaml
ttf:
  source:
    - source/Brill-Regular.input.ttf
    - source/Brill-Bold.input.ttf
  tables: [GDEF, GSUB, GPOS]
```

---

`glyphnames:` a file with source to final glyph naming map:

```yaml
glyphnames: source/BrillDev2Post.ren
```

---

`subsets`: a dictionary of font subset to create, the key is the stem of the subset file name, and the value is a dictionary of options similar to font options with two additional keys:

* `glyphlist`: the path of the file containing the subset glyph names, this is required
* `cmapoverride`: the path of a file containing overrides to the `cmap` table, in the form of space-sperated hex code point and glyphname pairs, e.g.: `1D00 a.smcp`

```yaml
subsets:
  BrillLatin-Regular:
    glyphlist: source/LatinSubset.txt
    cmapoverride: source/LatinSubsetCmap.txt
  BrillGreek-Regular:
    glyphlist: source/GreekSubset.txt
  BrillCyrillic-Regular:
    glyphlist: source/CyrillicSubset.txt
```

Note: glyph names in subset glyph lists and cmap override files must be post-renaming names.

---

`names:` entries at the top level will be shared across all the fonts, while `names:` entries at the font level will supplement or override the higher level `names:` entries. Note YAML syntax for multiline strings:

```yaml
names:
  11: https://www.tiro.com/
  13: |-
    Some multiline
    license text
```

Using `names:` to set the name table version string (ID 5) with the canonical format

```yaml
names:
  5: Version 1.20 ...
```
will update corresponding head table version and unique ID strings. It is recommended to use the YAML config file to rev build numbers when generating new fonts.

---

`vf-suffix:` Suffix to add to variable font family name. Updates also all related name table entries. Ignored for static fonts.

---

`set:` can be used to provide a bit value for the OS/2 table fstype field:

```yaml
set:
  fstype: [x]
```
fsType embedding bits are defined in the [OS/2 table spec](https://docs.microsoft.com/en-us/typography/opentype/spec/os2#fstype).

---

`DSIG:` can be used to add a stub digital signature table to fonts. Currently the only valid input is:

```yaml
DSIG: dummy
```

---

`components:` can be used to control how TTF composite glyphs are handled. Currently the only valid input is:

```yaml
components:
  decompose: overlapping
```

---

`formats:` a list of font formats to generate, possible values are: `ttf`, `otf`, `woff`, `woff2`. By default all formats are built:

```yaml
formats: [ttf, woff2]
```

---

`meta:` generates a `meta` table:

```yaml
meta:
  slng: [Latn, Grek, Cyrl]
  dlng: [Latn]
```

---

`STAT:` generates a `STAT` table. For variable fonts a basic `STAT` table is automatically built, but can be overridden here. The structure is a YAML representation of the input supported by FontTool’s [`buildStatTable`](https://fonttools.readthedocs.io/en/latest/otlLib/index.html#stat-table-builder):

```yaml
STAT:
  axes:
  - name: Weight
    tag: wght
    ordering: 0 # optional
    values:
    - name: Regular
      value: 400
      flags: 0x2 # optional
  - name: Width
    tag: wdth
    values:
    ...
  locations:
    name: Regular ABCD
    location:
      wght: 300
      ABCD: 100
  elidedFallbackName: Regular
```

---

Static instances can be also generated. To generate statics for all named instances:

```yaml
instances: all
```


To generate specific named instances:

```yaml
instances:
  Foo-Regular:
  Foo-Bold:
```

The instance key will be matched against named instances’ `postscriptNameID` and `subfamilyNameID`, e.g:

* `Foo-MediumItalic` will match named instance with PostScript name `Foo-MediumItalic` or with subfamily name `Medium Italic`.
* `Medium Italic` will also mach named instance with subfamily name `Medium Italic`.

Instances can also specify their coordinates, which does not require it being a named instance:

```yaml
instances:
  Foo-Slight:
    coordinates:
      wght: 112
```

They can also override `name` table entries:

```yaml
instances:
  Foo-Slight:
    coordinates:
      wght: 112
    names:
      1: Foo
      2: Slight
      6: Foo-Slight
```

---

`featureparams:` generates feature params or stylistic sets and character variants features. Feature params can be set whether the layout tables came from binary input fonts or from feature files. Optionally, the feature tag can include script and language, e.g. `ss01.latn` and `ss02.latn.ENG`:

```yaml
    featureparams:
      cv01:
        label: Alternate l
        tooltip: Alternates forms of the letter l
        sampletext: adhesiontext
        paramlabels:
          - Taller than capHeight
          - Serifed
          - Hooked
        characters: lĺłľḹl̃ļŀḷḻḽƚⱡ
      ss01: Serifed I and l
```

The `characters` key can be either a string (as above), or a list of
either characters or character codes, e.g.:

```yaml
characters: [l, 0x013A]
```

---

`autohinting:` control the TTF and OTF autohinting options. It currently supports to subkeys, `ttfautohint` and `psautohint`, ech accepts a `disable` key to disable the respective autohinter, e.g.:

```yaml
autohinting:
  ttfautohint:
    disable: true
  psautohint:
    disable: true
```

This can be set at project level or at font level, with the font-level settings
overriding the project-level ones.

`ttfautohint` additionally accepts the following set of keys (check TTFAutohint [documentation](https://freetype.org/ttfautohint/doc/ttfautohint.html) for the exact meaning of these keys):

* `control-file`: file path
* `reference-file`: file path
* `reference-index`: integer
* `reference-name`: string
* `hinting-range-min`: integer
* `hinting-range-max`: integer
* `hinting-limit`: integer
* `hint-composites`: `true` or `false`
* `adjust-subglyphs`: `true` or `false`
* `increase-x-height`: integer
* `x-height-snapping-exceptions`: string
* `windows-compatibility`: `true` or `false`
* `default-script`: string
* `fallback-script`: string
* `fallback-scaling`: `true` or `false`
* `symbol`: `true` or `false`
* `fallback-stem-width`: integer
* `ignore-restrictions`: `true` or `false`
* `family-suffix`: string
* `detailed-info`: `true` or `false`
* `no-info`: `true` or `false`
* `TTFA-info`: `true` or `false`
* `dehint`: `true` or `false`
* `epoch`: integer
* `debug`: `true` or `false`
* `verbose`: `true` or `false`

---

`gasp:` Controls gasp table. The value is a list of gasp ranges, each range sets `maxPPEM` value and `behavior` bits.

```yaml
gasp:
  - maxPPEM: 7
    behavior: [1, 3] # sets bits 1 and 3, GASP_DOGRAY and GASP_SYMMETRIC_SMOOTHING
  - maxPPEM: 65535
    behavior: [0, 1, 2, 3] # Sets all the defined bits
```
