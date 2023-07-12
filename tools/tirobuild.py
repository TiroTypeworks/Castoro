import logging
from copy import deepcopy
from enum import Enum
from pathlib import Path

import yaml

logger = logging.getLogger("builder")

PSNAMES_KEY = "public.postscriptNames"


class TemporaryLogLevel:
    def __init__(self, level):
        self.level = level
        self.logger = logging.getLogger()

    def __enter__(self):
        self.old = self.logger.level
        self.logger.setLevel(self.level)

    def __exit__(self, kind, value, tb):
        self.logger.setLevel(self.old)


class SaveState:
    def __init__(self, font):
        self.font = font

    def __enter__(self):
        self.name = self.font.name
        self.fmt = self.font.fmt
        self.variable = self.font.variable
        self.names = self.font.names
        self.STAT = self.font.STAT

    def __exit__(self, kind, value, tb):
        self.font.name = self.name
        self.font.fmt = self.fmt
        self.font.variable = self.variable
        self.font.names = self.names
        self.font.STAT = self.STAT


class Format(Enum):
    TTF = "ttf"
    OTF = "otf"
    WOFF = "woff"
    WOFF2 = "woff2"


def getName(font, nameID):
    name = font["name"].getName(nameID, platformID=3, platEncID=1, langID=0x409)
    if name:
        return str(name)
    return None


def setName(font, nameID, string):
    font["name"].setName(string, nameID, platformID=3, platEncID=1, langID=0x409)


def instanceMatch(key, instance, font):
    psname = getName(font, instance.postscriptNameID)
    if key == psname:
        return True
    subfamily = getName(font, instance.subfamilyNameID)
    if key == subfamily:
        return True
    if "-" in key:
        part = key.split("-", 1)[1]
        if subfamily == part:
            return True
        if subfamily.replace(" ", "") == part:
            return True
    return False


def instanceName(name, instance, font):
    psname = getName(font, instance.postscriptNameID)
    if psname:
        return psname

    subfamily = getName(font, instance.subfamilyNameID)
    return name.split("-")[0] + "-" + subfamily


class Font:
    def __init__(self, name, conf, project):
        self.name = name

        # Merge keys from the top level (project) configuration into the
        # current font’s conf.
        conf = {**conf}
        for key in project:
            if key == "fonts":
                continue
            if key not in conf:
                conf[key] = project[key]
            elif isinstance(project[key], dict):
                # We want to merge dictionaries from the two configurations, so
                # that, say, names can be set in the project and over-ridden by
                # the font’s conf.
                conf[key] = {**project[key], **conf[key]}

        self.source = conf.get("source")
        self.ren = conf.get("glyphnames")
        self.ttf = conf.get("ttf", {})

        path = conf["path"]
        self.output = path.parent / "output" / path.stem

        if self.source is None:
            raise RuntimeError(f"Can’t build {self.name} without a source")

        self.source = path.parent / self.source
        self.ren = path.parent / self.ren if self.ren else None

        self.variable = self.source.suffix == ".designspace"
        self.suffix = conf.get("vf-suffix")

        if "source" in self.ttf:
            if self.variable:
                if not isinstance(self.ttf["source"], list):
                    raise RuntimeError(f"TTF source must be list for variable fonts")
                self.ttf["source"] = [path.parent / p for p in self.ttf["source"]]
            else:
                self.ttf["source"] = path.parent / self.ttf["source"]

        self.subsets = {}
        for name, subset in conf.get("subsets", {}).items():
            if not "glyphlist" in subset:
                raise RuntimeError(f"Subset “{name}” did not provide a glyph list")
            glyphlist, tags = self._parsesubset(path.parent / subset["glyphlist"])
            subset["glyphlist"] = glyphlist
            subset["langsys"] = tags
            self.subsets[name] = subset

        self.names = conf.get("names", {})
        self.set = conf.get("set", {})

        self.DSIG = conf.get("DSIG")
        if "DSIG" in conf and self.DSIG != "dummy":
            raise RuntimeError(f"Only support “DSIG” value is “dummy”: “{self.DSIG}”")

        self.components = conf.get("components", {})

        self.meta = conf.get("meta", [])

        self.formats = [Format(f) for f in conf.get("formats", list(Format))]
        self.fmt = None

        self.instances = conf.get("instances")
        if self.instances is not None:
            if self.instances == "all":
                self.instances = {}
            if not isinstance(self.instances, dict):
                raise RuntimeError(f"Unsupported “instances” value: “{self.instances}”")

        self.STAT = conf.get("STAT")
        if self.STAT:
            if not "axes" in self.STAT:
                raise RuntimeError("“STAT” table must have “axes”")

        self.featureparams = conf.get("featureparams", {})
        if not isinstance(self.featureparams, dict):
            raise RuntimeError("“featureparams” must be a dictionary")
        for tag, params in self.featureparams.items():
            if (
                tag.startswith("ss")
                and tag[2:].isnumeric()
                and int(tag[2:]) in range(1, 21)
            ):
                if not isinstance(params, str):
                    raise RuntimeError(
                        "“featureparams” of stylistic set must be a string"
                    )
            elif (
                tag.startswith("cv")
                and tag[2:].isnumeric()
                and int(tag[2:]) in range(1, 100)
            ):
                if not isinstance(params, dict):
                    raise RuntimeError(
                        "“featureparams” of character variant must be a dictionary"
                    )
            else:
                raise RuntimeError(
                    f"“featureparams” are unsupported for feature: {tag}"
                )

    @property
    def ext(self):
        return self.fmt.value

    @property
    def filename(self):
        return self.name + "." + self.ext

    def _parsesubset(self, subset):
        with open(subset) as f:
            lines = f.read().split("\n")

        glyphlist = set()
        tags = set()
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith("#"):
                if i == 0:
                    _, tags = line.split("#", 1)
                    tags = {t.strip() for t in tags.split(",")}
            else:
                glyphlist.add(line)

        return (glyphlist, tags if tags else ["*"])

    def _openufo(self, path, dspath=None):
        from ufoLib2 import Font as UFOFont

        if not path.exists() and dspath is not None:
            path = dspath.parent / path.name

        ufo = UFOFont.open(path, validate=False)

        if self.ren is not None:
            with open(self.ren, "r") as f:
                logger.info(f"Setting {path.name} final glyph names")
                lines = f.read().split("\n")
                lines = [l.split() for l in lines if l and not l.startswith("%")]
                ufo.lib[PSNAMES_KEY] = {l[0]: l[1] for l in lines}

        if "fstype" in self.set:
            ufo.info.openTypeOS2Type = self.set["fstype"]

        return ufo

    def _setfeatureparams(self, otf):
        if not self.featureparams:
            return

        from fontTools.ttLib.tables import otTables

        logger.info(f"Adding “featureParams” to {self.filename}")
        name = otf["name"]

        def addName(string):
            if not string:
                return 0
            if isinstance(string, str):
                return name.addMultilingualName({"en": string}, mac=False)
            elif isinstance(string, list):
                nameid = name.addMultilingualName({"en": string[0]}, mac=False)
                for s in string[1:]:
                    name.addMultilingualName({"en": s}, mac=False)
                return nameid

        for tag in ("GSUB", "GPOS"):
            if tag not in otf:
                continue
            table = otf[tag].table
            for feature in table.FeatureList.FeatureRecord:
                if feature.FeatureTag in self.featureparams:
                    conf = self.featureparams[feature.FeatureTag]
                    if feature.FeatureTag.startswith("ss"):
                        params = otTables.FeatureParamsStylisticSet()
                        params.Version = 0
                        params.UINameID = addName(conf)
                    elif feature.FeatureTag.startswith("cv"):
                        label = conf.get("label")
                        tooltip = conf.get("tooltip")
                        sampletext = conf.get("sampletext")
                        paramlabels = conf.get("paramlabels", [])
                        characters = conf.get("characters", [])
                        if isinstance(characters, str):
                            characters = [ord(c) for c in characters]
                        else:
                            characters = [
                                ord(c) if isinstance(c, str) else c for c in characters
                            ]

                        params = otTables.FeatureParamsCharacterVariants()
                        params.Format = 0
                        params.FeatUILabelNameID = addName(label)
                        params.FeatUITooltipTextNameID = addName(tooltip)
                        params.SampleTextNameID = addName(sampletext)
                        params.NumNamedParameters = len(paramlabels)
                        params.FirstParamUILabelNameID = addName(paramlabels)
                        params.Character = characters
                        params.CharCount = len(characters)
                    feature.Feature.FeatureParams = params

    def _setstat(self, font):
        if self.STAT:
            from fontTools.otlLib.builder import buildStatTable

            logger.info(f"Adding “STAT” table to {self.filename}")
            buildStatTable(
                font,
                axes=self.STAT["axes"],
                locations=self.STAT.get("locations"),
                elidedFallbackName=self.STAT.get("elidedFallbackName", 2),
            )
        elif self.variable:
            from axisregistry import build_stat

            logger.info(f"Adding default “STAT” table to {self.filename}")
            build_stat(font)

    def _copytables(self, otf, otl):
        from fontTools.otlLib.maxContextCalc import maxCtxFont

        otl.setGlyphOrder(otf.getGlyphOrder())
        for tag in self.ttf.get("tables", []):
            logger.info(f"Copying “{tag}” table to {self.filename}")
            otf[tag] = deepcopy(otl[tag])
        otf["OS/2"].usMaxContext = maxCtxFont(otf)

        return otf

    def _postprocess(self, otf):
        self._setnames(otf)

        if self.DSIG:
            from fontTools.ttLib import newTable

            logger.info(f"Adding “DSIG” table to {self.filename}")
            otf["DSIG"] = DSIG = newTable("DSIG")
            DSIG.ulVersion = 1
            DSIG.usFlag = 0
            DSIG.usNumSigs = 0
            DSIG.signatureRecords = []

        if self.meta:
            from fontTools.ttLib import newTable

            logger.info(f"Adding “meta” table to {self.filename}")
            otf["meta"] = meta = newTable("meta")
            meta.data = {t: ",".join(v) for t, v in self.meta.items()}

        self._setstat(otf)
        self._setfeatureparams(otf)

        return otf

    def _autohint(self, otf):
        from fontTools.ttLib import TTFont

        logger.info(f"Autohinting {self.filename}")
        if self.fmt == Format.TTF and not self.variable:
            from io import BytesIO

            from ttfautohint import ttfautohint

            buf = BytesIO()
            otf.save(buf)
            otf.close()
            data = ttfautohint(in_buffer=buf.getvalue(), no_info=True)
            otf = TTFont(BytesIO(data))

            # Set bit 3 on head.flags
            # https://font-bakery.readthedocs.io/en/latest/fontbakery/profiles/googlefonts.html#com.google.fonts/check/integer_ppem_if_hinted
            head = otf["head"]
            head.flags |= 1 << 3
        elif self.fmt == Format.OTF:
            from tempfile import TemporaryDirectory

            from psautohint.__main__ import main as psautohint

            with TemporaryDirectory() as d:
                path = Path(d) / "tmp.otf"
                otf.save(path)
                with TemporaryLogLevel(logging.ERROR):
                    psautohint([str(path)])
                otf.close()
                otf = TTFont(path)
        return otf

    def _subset(self, otf):
        from fontTools.subset import Options, Subsetter

        for name, subset in self.subsets.items():
            with SaveState(self):
                self.name = name
                logger.info(f"Creating {self.filename} subset")
                new = deepcopy(otf)
                options = Options()
                options.name_IDs = ["*"]
                options.name_legacy = True
                options.name_languages = ["*"]
                options.recommended_glyphs = True
                options.layout_features = ["*"]
                options.notdef_outline = True
                options.notdef_glyph = True
                options.glyph_names = True
                options.hinting = True
                options.legacy_kern = True
                options.symbol_cmap = True
                options.layout_closure = False
                options.prune_unicode_ranges = False
                options.passthrough_tables = False
                options.recalc_average_width = True
                options.ignore_missing_glyphs = True
                options.layout_scripts = subset["langsys"]

                options.drop_tables.remove("DSIG")
                options.no_subset_tables += ["DSIG", "meta"]

                subsetter = Subsetter(options=options)
                subsetter.populate(subset["glyphlist"])

                with TemporaryLogLevel(logging.WARNING):
                    subsetter.subset(new)

                self.names = subset.get("names")
                new = self._optimize(new)
                self._setnames(new)
                self._instanciate(new)
                self._buildwoff(new)
                self._save(new)

    def _instanciate(self, vf):
        if self.instances is None or not self.variable:
            return

        from io import BytesIO

        from fontTools.ttLib import TTFont
        from fontTools.varLib.instancer import setRibbiBits
        from fontTools.varLib.instancer.names import pruningUnusedNames, updateNameTable
        from fontTools.varLib.mutator import instantiateVariableFont

        logger.info(f"Instancing {self.filename} statics")
        instances = []
        if not self.instances:
            for instance in vf["fvar"].instances:
                name = instanceName(self.name, instance, vf)
                conf = {"name": name.replace(" ", "")}
                instances.append((instance.coordinates, conf))
        else:
            for key, conf in self.instances.items():
                conf = conf if isinstance(conf, dict) else {}
                conf["name"] = key
                if "coordinates" in conf:
                    instances.append((conf["coordinates"], conf))
                    continue
                for instance in vf["fvar"].instances:
                    if instanceMatch(key, instance, vf):
                        instances.append((instance.coordinates, conf))
                        break

        for coordinates, conf in instances:
            stream = BytesIO()
            vf.save(stream)
            stream.seek(0)
            otf = TTFont(stream)

            try:
                updateNameTable(otf, coordinates)
            except ValueError:
                pass

            with SaveState(self):
                self.name = conf["name"]
                logger.info(f"Instancing {self.filename}")
                self.variable = False
                self.STAT = None
                with pruningUnusedNames(otf):
                    otf = instantiateVariableFont(otf, coordinates, inplace=True)
                otf["name"].removeNames(25)
                setRibbiBits(otf)
                self.names = conf.get("names")
                self._postprocess(otf)
                self._save(otf)
                self._buildwoff(otf)

    def _setnames(self, font):
        font["name"].names = [n for n in font["name"].names if n.platformID == 3]
        if not self.names:
            return

        logger.info(f"Adding “name” entries to {self.filename}")

        # Make a copy as we might modify it.
        names = self.names.copy()

        # If version or psname IDs are specified, but unique ID is not, update
        # the later.
        if (5 in names or 6 in names) and (3 not in names):
            version = names.get(5, getName(font, 5))
            psname = names.get(6, getName(font, 6))
            vendor = font["OS/2"].achVendID
            names[3] = f"{version.replace('Version ', '')}:{vendor}:{psname}"

        for nameID, string in names.items():
            setName(font, nameID, string)

        if 5 in names:
            import re

            m = re.match("Version (\d\.\d\d)", names[5])
            if m is None:
                raise ValueError(f"Can’t parse version string: {names[5]}")
            font["head"].fontRevision = float(m.group(1))

        if "CFF " in font and any(n in names for n in (0, 1, 4, 5, 6, 7)):
            cff = font["CFF "].cff
            cff.fontNames[0] = names.get(6, cff.fontNames[0])
            topDict = cff.topDictIndex[0]
            topDict.Copyright = names.get(0, topDict.Copyright)
            topDict.FamilyName = names.get(1, topDict.FamilyName)
            topDict.FullName = names.get(4, topDict.FullName)
            topDict.Notice = names.get(7, topDict.Notice)
            if 5 in names:
                topDict.version = f"{font['head'].fontRevision}"

    def _optimize(self, otf):
        if "CFF " in otf:
            import cffsubr
            from fontTools.cffLib.specializer import specializeProgram

            logger.info(f"Optimizing {self.filename}")
            topDict = otf["CFF "].cff.topDictIndex[0]
            charStrings = topDict.CharStrings
            for charString in charStrings.values():
                charString.decompile()
                charString.program = specializeProgram(charString.program)

            logger.info(f"Subroutinizing {self.filename}")
            cffsubr.subroutinize(otf, keep_glyph_names=False)
        return otf

    def _addvfsuffix(self, otf):
        names = {}

        if self.variable and self.suffix:
            family = None

            # Find the family name, we need it to know where to insert the
            # suffix in full names
            for record in otf["name"].names:
                if record.nameID == 16:
                    family = str(record)
                elif record.nameID == 1 and family is None:
                    family = str(record)

            for record in otf["name"].names:
                if record.nameID in [1, 16, 21]:
                    # Family names, append space then the suffix
                    names[record.nameID] = f"{str(record)} {self.suffix}"
                if record.nameID == 6:
                    # PostScript name, append suffix to family name
                    psfamily = family.replace(" ", "")
                    vfpsfamily = f"{psfamily}{self.suffix}"
                    names[record.nameID] = str(record).replace(psfamily, vfpsfamily)
                if record.nameID in [4, 18]:
                    # Full names, append space then the suffix to family name
                    vffamily = f"{family} {self.suffix}"
                    names[record.nameID] = str(record).replace(family, vffamily)

        with SaveState(self):
            self.names = names
            self._setnames(otf)

    def _buildwoff(self, otf):
        for fmt in self.formats:
            if fmt not in (Format.WOFF, Format.WOFF2):
                continue
            new = deepcopy(otf)
            new.flavor = fmt.value
            self._save(new, fmt)

    def _save(self, otf, wfmt=None):
        fmt = self.fmt
        fmtdir = fmt.name
        if self.variable:
            fmtdir += "VF"
        if wfmt is not None:
            fmtdir += wfmt.name
            self.fmt = wfmt
        parent = self.output / self.name.split("-")[0] / fmtdir
        parent.mkdir(parents=True, exist_ok=True)
        path = parent / self.filename
        logger.info(f"Saving {path}")
        otf.save(path)
        self.fmt = fmt

    def build(self):
        logger.info(f"Building {self.name}")
        with SaveState(self):
            if self.variable:
                self._buildvariable()
            else:
                self._buildstatic()

    def _buildvariable(self):
        from fontTools.designspaceLib import DesignSpaceDocument
        from fontTools.varLib import build as buildvf
        from ufo2ft import (
            compileInterpolatableOTFsFromDS,
            compileInterpolatableTTFsFromDS,
        )

        ds = DesignSpaceDocument.fromfile(self.source)
        ds.loadSourceFonts(lambda p: self._openufo(Path(p), self.source))

        for fmt in self.formats:
            self.fmt = fmt
            if fmt == Format.TTF:
                compileFont = compileInterpolatableTTFsFromDS
            elif fmt == Format.OTF:
                compileFont = compileInterpolatableOTFsFromDS
            else:
                continue

            otfds = compileFont(ds, inplace=False)

            if "source" in self.ttf:
                from fontTools.ttLib import TTFont

                if len(otfds.sources) != len(self.ttf["source"]):
                    raise RuntimeError(f"TTF sources must equal DesignSpace sources")

                for i, source in enumerate(otfds.sources):
                    otl = TTFont(self.ttf["source"][i])
                    with SaveState(self):
                        self.name = Path(source.path).stem
                        source.font = self._copytables(source.font, otl)

            vf, _, _ = buildvf(otfds)

            vf = self._postprocess(vf)
            vf = self._autohint(vf)
            self._subset(vf)
            self._instanciate(vf)
            self._addvfsuffix(vf)
            vf = self._optimize(vf)
            self._buildwoff(vf)
            self._save(vf)

    def _buildstatic(self):
        from ufo2ft import compileOTF, compileTTF

        ufo = self._openufo(self.source)

        for fmt in (Format.TTF, Format.OTF):
            self.fmt = fmt
            options = {}
            if fmt == Format.TTF:
                compileFont = compileTTF
            elif fmt == Format.OTF:
                compileFont = compileOTF
                options["optimizeCFF"] = False
            else:
                continue

            options["removeOverlaps"] = True
            options["overlapsBackend"] = "pathops"
            if set(self.ttf.get("tables", {})) == {"GDEF", "GSUB", "GPOS"}:
                options["featureWriters"] = []

            otf = compileFont(
                ufo,
                **options,
            )

            if (
                fmt == Format.TTF
                and "decompose" in self.components
                and self.components["decompose"] == "overlapping"
            ):
                from fontTools.ttLib.removeOverlaps import removeTTGlyphOverlaps

                # Decompose composite glyphs with overlapping components, and
                # remove overelap. We already decomposed simple glyphs while
                # building the font, so we process only composite glyphs below.
                # The removeTTGlyphOverlaps function only decomposes composites
                # with overlapping components, so we don’t check for the
                # overlap ourselves.
                logger.info(f"Decomposing {self.name} overlapping components")
                glyf = otf["glyf"]
                hmtx = otf["hmtx"]
                glyphSet = otf.getGlyphSet()
                glyphOrder = otf.getGlyphOrder()
                for name in glyphOrder:
                    glyph = glyf[name]
                    if glyph.isComposite():
                        removeTTGlyphOverlaps(name, glyphSet, glyf, hmtx, False)

            if "source" in self.ttf:
                from fontTools.ttLib import TTFont

                otl = TTFont(self.ttf["source"])
                otf = self._copytables(otf, otl)

            otf = self._postprocess(otf)
            otf = self._autohint(otf)
            self._subset(otf)
            otf = self._optimize(otf)
            self._buildwoff(otf)
            self._save(otf)


class Builder:
    def __init__(self, path):
        with open(path) as f:
            project = yaml.safe_load(f)
            project["path"] = path

        if project.get("fonts", None) is None:
            raise RuntimeError(f"Missing or empty top level “fonts:” key.")

        self.fonts = []
        for name, conf in project.get("fonts", {}).items():
            self.fonts.append(Font(name, conf, project))

        if not self.fonts:
            raise RuntimeError(f"There are no fonts in the project.")

    def build(self):
        for font in self.fonts:
            font.build()


class ColorLogFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: "\x1b[38;21m",
        logging.INFO: "\x1b[1;32m",
        logging.WARNING: "\x1b[33;21m",
        logging.ERROR: "\x1b[31;21m",
        logging.CRITICAL: "\x1b[31;1m",
    }
    RESET = "\x1b[0m"

    def format(self, record):
        color = self.COLORS[record.levelno]
        name = "[\x1b[33;21m%(name)s\x1b[0m]"
        fmt = f"{color}%(levelname)s{self.RESET}\t%(message)s {name}"
        return logging.Formatter(fmt).format(record)


def main(args=None):
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Build Tiro fonts.")
    parser.add_argument("project", metavar="PROJECT", help="Project file.", type=Path)
    parser.add_argument("-q", "--quite", action="store_true", help="Be quite")
    options = parser.parse_args(args)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(ColorLogFormatter())
    if options.quite:
        logging.basicConfig(level=logging.WARNING, handlers=[ch])
    else:
        logging.basicConfig(level=logging.INFO, handlers=[ch])

    builder = Builder(options.project)
    builder.build()


if __name__ == "__main__":
    import sys

    sys.exit(main())
