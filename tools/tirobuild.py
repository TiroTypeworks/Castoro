import logging
from copy import deepcopy
from enum import Enum
from pathlib import Path
from types import SimpleNamespace

import yaml
from fontTools.otlLib.maxContextCalc import maxCtxFont
from fontTools.ttLib import TTFont, newTable
from ufo2ft import compileOTF, compileTTF
from ufoLib2 import Font as UFOFont

logger = logging.getLogger("builder")

PSNAMES_KEY = "public.postscriptNames"


def _guess_format(path):
    if path.suffix == ".ttf":
        return Format.TTF
    elif path.suffix == ".otf":
        return Format.OTF
    else:
        raise ValueError(f"Unknown font format for {path}")


class TemporaryLogLevel:
    def __init__(self, level):
        self.level = level
        self.logger = logging.getLogger()

    def __enter__(self):
        self.old = self.logger.level
        self.logger.setLevel(self.level)

    def __exit__(self, kind, value, tb):
        self.logger.setLevel(self.old)


class Format(Enum):
    TTF = "ttf"
    OTF = "otf"
    WOFF = "woff"
    WOFF2 = "woff2"
    VARTTF = "variable"
    VAROTF = "variable-cff2"


class Font:
    def __init__(self, name, conf, project):
        self.name = name

        conf = {**project, **conf}
        self.source = conf.get("source", None)
        self.ren = conf.get("glyphnames", None)
        self.ttf = conf.get("ttf", {})

        path = conf["path"]
        self.output = path.parent / "output" / path.stem

        if self.source is None:
            raise RuntimeError(f"Can’t build {self.name} without a source")

        self.source = path.parent / self.source
        self.ren = path.parent / self.ren if self.ren else None
        if "source" in self.ttf:
            self.ttf["source"] = path.parent / self.ttf["source"]

        self.subsets = {}
        for name, subset in conf.get("subsets", {}).items():
            if not "glyphlist" in subset:
                raise RuntimeError(f"Subset {name} did not provide a glyph list")
            glyphlist, tags = self._parsesubset(path.parent / subset["glyphlist"])
            subset["glyphlist"] = glyphlist
            subset["langsys"] = tags
            self.subsets[name] = subset

        self.names = conf.get("names", {})
        self.set = conf.get("set", {})

        self.DSIG = conf.get("DSIG", None)
        if "DSIG" in conf and self.DSIG != "dummy":
            raise RuntimeError(f"Only “dummy” DSIG table is supported: “{self.DSIG}”")

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

    def _preprocess(self):
        ufo = UFOFont.open(self.source, validate=False)

        if self.ren is not None:
            with open(self.ren, "r") as f:
                logger.info(f"Setting {self.name} final glyph names")
                lines = f.read().split("\n")
                lines = [l.split() for l in lines if l and not l.startswith("%")]
                ufo.lib[PSNAMES_KEY] = {l[0]: l[1] for l in lines}

        if "fstype" in self.set:
            ufo.info.openTypeOS2Type = self.set["fstype"]

        otl = TTFont(self.ttf["source"]) if "source" in self.ttf else None

        return ufo, otl

    def _postprocess(self, otf, otl, fmt):
        if otl is not None:
            otl.setGlyphOrder(otf.getGlyphOrder())
            for tag in self.ttf.get("tables", []):
                logger.info(f"Copying {tag} table to {self.name}.{fmt.value}")
                otf[tag] = deepcopy(otl[tag])
            otf["OS/2"].usMaxContext = maxCtxFont(otf)

        if self.names:
            logger.info(f"Adding name entries to {self.name}.{fmt.value}")
            self._setnames(otf, self.names)

        if self.DSIG:
            otf["DSIG"] = DSIG = newTable("DSIG")
            DSIG.ulVersion = 1
            DSIG.usFlag = 0
            DSIG.usNumSigs = 0
            DSIG.signatureRecords = []

        return otf

    def _autohint(self, otf, fmt):
        logger.info(f"Autohinting {self.name}.{fmt.value}")
        if fmt == Format.TTF:
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
        elif fmt == Format.OTF:
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

    def _subset(self, otf, fmt):
        from fontTools.subset import Options, Subsetter

        for name, subset in self.subsets.items():
            logger.info(f"Creating {name}.{fmt.value} subset")
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
            options.no_subset_tables += ["DSIG"]

            subsetter = Subsetter(options=options)
            subsetter.populate(subset["glyphlist"])

            with TemporaryLogLevel(logging.WARNING):
                subsetter.subset(new)

            new = self._optimize(new, name, fmt)
            names = subset.get("names")
            if names:
                logger.info(f"Adding name entries to {name}.{fmt.value} susbet")
                self._setnames(new, names)
            self._buildwoff(new, name, fmt)
            self._save(new, name, fmt)

    def _setnames(self, font, names):
        # Make a copy as we might modify it.
        names = names.copy()

        # If version or psname IDs are specified, but unique ID is not, update
        # the later.
        if (5 in names or 6 in names) and (3 not in names):
            version = names.get(5, str(font["name"].getName(5, 3, 1)))
            psname = names.get(6, str(font["name"].getName(6, 3, 1)))
            vendor = font["OS/2"].achVendID
            names[3] = f"{version.replace('Version ', '')}:{vendor}:{psname}"

        for nameID, string in names.items():
            font["name"].setName(
                string, nameID, platformID=3, platEncID=1, langID=0x409
            )

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

    def _optimize(self, otf, name, fmt):
        if fmt == Format.OTF:
            import cffsubr
            from fontTools.cffLib.specializer import specializeProgram

            logger.info(f"Optimizing {name}.{fmt.value}")
            topDict = otf["CFF "].cff.topDictIndex[0]
            charStrings = topDict.CharStrings
            for charString in charStrings.values():
                charString.decompile()
                charString.program = specializeProgram(charString.program)

            logger.info(f"Subroutinizing {name}.{fmt.value}")
            cffsubr.subroutinize(otf, keep_glyph_names=False)
        return otf

    def _buildwoff(self, otf, name, fmt):
        for wfmt in (Format.WOFF, Format.WOFF2):
            new = deepcopy(otf)
            new.flavor = wfmt.value
            self._save(new, name, fmt, wfmt)

    def _save(self, otf, name, fmt, wfmt=None):
        parent = self.output / name.split("-")[0] / fmt.name
        if wfmt is not None:
            parent = parent.with_name(fmt.name + wfmt.name)
            fmt = wfmt
        parent.mkdir(parents=True, exist_ok=True)
        path = parent / f"{name}.{fmt.value}"
        logger.info(f"Saving {path}")
        otf.save(path)

    def build(self):
        logger.info(f"Building {self.name}")
        ufo, otl = self._preprocess()

        for fmt in (Format.TTF, Format.OTF):
            options = {}
            if set(self.ttf.get("tables", {})) == {"GDEF", "GSUB", "GPOS"}:
                options["featureWriters"] = []

            if fmt == Format.TTF:
                compileFont = compileTTF
            elif fmt == Format.OTF:
                compileFont = compileOTF
                options["optimizeCFF"] = False

            otf = compileFont(
                ufo,
                removeOverlaps=True,
                overlapsBackend="pathops",
                **options,
            )

            otf = self._postprocess(otf, otl, fmt)
            otf = self._autohint(otf, fmt)
            self._subset(otf, fmt)
            otf = self._optimize(otf, self.name, fmt)
            self._buildwoff(otf, self.name, fmt)
            self._save(otf, self.name, fmt)


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
    options = parser.parse_args(args)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(ColorLogFormatter())
    logging.basicConfig(level=logging.INFO, handlers=[ch])

    builder = Builder(options.project)
    builder.build()


if __name__ == "__main__":
    import sys

    sys.exit(main())
