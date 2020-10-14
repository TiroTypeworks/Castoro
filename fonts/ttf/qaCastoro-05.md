## Fontbakery report

Fontbakery version: 0.7.31

<details>
<summary><b>[4] Castoro-Italic.ttf</b></summary>
<details>
<summary>⚠ <b>WARN:</b> Check if each glyph has the recommended amount of contours.</summary>

* [com.google.fonts/check/contour_count](https://font-bakery.readthedocs.io/en/latest/fontbakery/profiles/googlefonts.html#com.google.fonts/check/contour_count)
<pre>--- Rationale ---

Visually QAing thousands of glyphs by hand is tiring. Most glyphs can only be
constructured in a handful of ways. This means a glyph&#x27;s contour count will
only differ slightly amongst different fonts, e.g a &#x27;g&#x27; could either be 2 or 3
contours, depending on whether its double story or single story.

However, a quotedbl should have 2 contours, unless the font belongs to a
display family.

This check currently does not cover variable fonts because there&#x27;s plenty of
alternative ways of constructing glyphs with multiple outlines for each feature
in a VarFont. The expected contour count data for this check is currently
optimized for the typical construction of glyphs in static fonts.


</pre>

* ⚠ **WARN** This check inspects the glyph outlines and detects the total number of contours in each of them. The expected values are infered from the typical ammounts of contours observed in a large collection of reference font families. The divergences listed below may simply indicate a significantly different design on some of your glyphs. On the other hand, some of these may flag actual bugs in the font such as glyphs mapped to an incorrect codepoint. Please consider reviewing the design and codepoint assignment of these to make sure they are correct.

The following glyphs do not have the recommended number of contours:

Glyph name: softhyphen	Contours detected: 0	Expected: 1
Glyph name: Uogonek	Contours detected: 2	Expected: 1
Glyph name: ZWNJ	Contours detected: 1	Expected: 0
Glyph name: ZWJ	Contours detected: 2	Expected: 0
Glyph name: Uogonek	Contours detected: 2	Expected: 1
Glyph name: rupee	Contours detected: 1	Expected: 3 [code: contour-count]

</details>
<details>
<summary>⚠ <b>WARN:</b> Font has **proper** whitespace glyph names?</summary>

* [com.google.fonts/check/whitespace_glyphnames](https://font-bakery.readthedocs.io/en/latest/fontbakery/profiles/universal.html#com.google.fonts/check/whitespace_glyphnames)
<pre>--- Rationale ---

This check enforces adherence to recommended whitespace (codepoints 0020 and
00A0) glyph names according to the Adobe Glyph List.


</pre>

* ⚠ **WARN** Glyph 0x00A0 is called "nbspace": Change to "uni00A0" [code: not-recommended-00a0]

</details>
<details>
<summary>⚠ <b>WARN:</b> Glyph names are all valid?</summary>

* [com.google.fonts/check/valid_glyphnames](https://font-bakery.readthedocs.io/en/latest/fontbakery/profiles/universal.html#com.google.fonts/check/valid_glyphnames)
<pre>--- Rationale ---

Microsoft&#x27;s recommendations for OpenType Fonts states the following:

&#x27;NOTE: The PostScript glyph name must be no longer than 31 characters, include
only uppercase or lowercase English letters, European digits, the period or the
underscore, i.e. from the set [A-Za-z0-9_.] and should start with a letter,
except the special glyph name &quot;.notdef&quot; which starts with a period.&#x27;

https://docs.microsoft.com/en-us/typography/opentype/spec/recom#post-table


In practice, though, particularly in modern environments, glyph names can be as
long as 63 characters.
According to the &quot;Adobe Glyph List Specification&quot; available at:

https://github.com/adobe-type-tools/agl-specification


</pre>

* ⚠ **WARN** The following glyph names may be too long for some legacy systems which may expect a maximum 31-char length limit:
L_ringbelowcomb_macroncomb_acutecomb, R_ringbelowcomb_macroncomb_acutecomb, G_macronbelowcomb_H_macronbelowcomb, l_ringbelowcomb_macroncomb_acutecomb, r_ringbelowcomb_macroncomb_acutecomb, L_ringbelowcomb_macroncomb_acutecomb.sc, R_ringbelowcomb_macroncomb_acutecomb.sc and G_macronbelowcomb_H_macronbelowcomb.sc [code: legacy-long-names]

</details>
<details>
<summary>⚠ <b>WARN:</b> Checking Vertical Metric Linegaps.</summary>

* [com.google.fonts/check/linegaps](https://font-bakery.readthedocs.io/en/latest/fontbakery/profiles/hhea.html#com.google.fonts/check/linegaps)

* ⚠ **WARN** hhea lineGap is not equal to 0. [code: hhea]

</details>
<br>
</details>
<details>
<summary><b>[4] Castoro-Regular.ttf</b></summary>
<details>
<summary>⚠ <b>WARN:</b> Check if each glyph has the recommended amount of contours.</summary>

* [com.google.fonts/check/contour_count](https://font-bakery.readthedocs.io/en/latest/fontbakery/profiles/googlefonts.html#com.google.fonts/check/contour_count)
<pre>--- Rationale ---

Visually QAing thousands of glyphs by hand is tiring. Most glyphs can only be
constructured in a handful of ways. This means a glyph&#x27;s contour count will
only differ slightly amongst different fonts, e.g a &#x27;g&#x27; could either be 2 or 3
contours, depending on whether its double story or single story.

However, a quotedbl should have 2 contours, unless the font belongs to a
display family.

This check currently does not cover variable fonts because there&#x27;s plenty of
alternative ways of constructing glyphs with multiple outlines for each feature
in a VarFont. The expected contour count data for this check is currently
optimized for the typical construction of glyphs in static fonts.


</pre>

* ⚠ **WARN** This check inspects the glyph outlines and detects the total number of contours in each of them. The expected values are infered from the typical ammounts of contours observed in a large collection of reference font families. The divergences listed below may simply indicate a significantly different design on some of your glyphs. On the other hand, some of these may flag actual bugs in the font such as glyphs mapped to an incorrect codepoint. Please consider reviewing the design and codepoint assignment of these to make sure they are correct.

The following glyphs do not have the recommended number of contours:

Glyph name: softhyphen	Contours detected: 0	Expected: 1
Glyph name: Uogonek	Contours detected: 2	Expected: 1
Glyph name: ZWNJ	Contours detected: 1	Expected: 0
Glyph name: ZWJ	Contours detected: 2	Expected: 0
Glyph name: Uogonek	Contours detected: 2	Expected: 1
Glyph name: rupee	Contours detected: 1	Expected: 3 [code: contour-count]

</details>
<details>
<summary>⚠ <b>WARN:</b> Font has **proper** whitespace glyph names?</summary>

* [com.google.fonts/check/whitespace_glyphnames](https://font-bakery.readthedocs.io/en/latest/fontbakery/profiles/universal.html#com.google.fonts/check/whitespace_glyphnames)
<pre>--- Rationale ---

This check enforces adherence to recommended whitespace (codepoints 0020 and
00A0) glyph names according to the Adobe Glyph List.


</pre>

* ⚠ **WARN** Glyph 0x00A0 is called "nbspace": Change to "uni00A0" [code: not-recommended-00a0]

</details>
<details>
<summary>⚠ <b>WARN:</b> Glyph names are all valid?</summary>

* [com.google.fonts/check/valid_glyphnames](https://font-bakery.readthedocs.io/en/latest/fontbakery/profiles/universal.html#com.google.fonts/check/valid_glyphnames)
<pre>--- Rationale ---

Microsoft&#x27;s recommendations for OpenType Fonts states the following:

&#x27;NOTE: The PostScript glyph name must be no longer than 31 characters, include
only uppercase or lowercase English letters, European digits, the period or the
underscore, i.e. from the set [A-Za-z0-9_.] and should start with a letter,
except the special glyph name &quot;.notdef&quot; which starts with a period.&#x27;

https://docs.microsoft.com/en-us/typography/opentype/spec/recom#post-table


In practice, though, particularly in modern environments, glyph names can be as
long as 63 characters.
According to the &quot;Adobe Glyph List Specification&quot; available at:

https://github.com/adobe-type-tools/agl-specification


</pre>

* ⚠ **WARN** The following glyph names may be too long for some legacy systems which may expect a maximum 31-char length limit:
L_ringbelowcomb_macroncomb_acutecomb, R_ringbelowcomb_macroncomb_acutecomb, G_macronbelowcomb_H_macronbelowcomb, l_ringbelowcomb_macroncomb_acutecomb, r_ringbelowcomb_macroncomb_acutecomb, L_ringbelowcomb_macroncomb_acutecomb.sc, R_ringbelowcomb_macroncomb_acutecomb.sc and G_macronbelowcomb_H_macronbelowcomb.sc [code: legacy-long-names]

</details>
<details>
<summary>⚠ <b>WARN:</b> Checking Vertical Metric Linegaps.</summary>

* [com.google.fonts/check/linegaps](https://font-bakery.readthedocs.io/en/latest/fontbakery/profiles/hhea.html#com.google.fonts/check/linegaps)

* ⚠ **WARN** hhea lineGap is not equal to 0. [code: hhea]

</details>
<br>
</details>

### Summary

| 💔 ERROR | 🔥 FAIL | ⚠ WARN | 💤 SKIP | ℹ INFO | 🍞 PASS | 🔎 DEBUG |
|:-----:|:----:|:----:|:----:|:----:|:----:|:----:|
| 0 | 0 | 8 | 179 | 12 | 149 | 0 |
| 0% | 0% | 2% | 51% | 3% | 43% | 0% |

**Note:** The following loglevels were omitted in this report:
* **SKIP**
* **INFO**
* **PASS**
* **DEBUG**
