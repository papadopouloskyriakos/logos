"""Adversarial unit tests for the Linear A sign-inventory ontology
(scripts/inventory/build_ontology.py + floor_cleaned.py).

Covers, per the verification brief:
  1. CLASSIFICATION -- every canonical sign has a functional_class; AB-series
     (shared with Linear B, known values) are separated from A-only (*-series);
     logograms / numerals / fractions are excluded from the syllabogram stream;
     ambiguous tokens are 'uncertain', not forced.
  2. NESTING -- the three inventories are layered (raw -> conservative ->
     exploratory) in the meaningful sense (every id is a merge-image of the
     layer above), with the literal-set caveat documented.
  3. FLOOR -- the information floor on the cleaned syllabogram stream is
     recomputed with the SAME formula as scripts/corpus_info.py and is
     arithmetically self-consistent (U = H(K)/D, D = log2(V) - H_rate).

Two findings are recorded as xfail regression tests so they surface the day
they are fixed:
  * `*OLIV` and `*406VAS` (star-prefixed logograms) leak into the RAW
    syllabogram stream -- `_classify_head` defaults any `*<non-digit, non-FM>`
    token to syllabogram-Aonly instead of recognising the embedded ideogram.
    The PRIMARY conservative stream is unaffected (the confidence filter
    excludes them as ligature-only), so this contaminates only the V=131
    sensitivity number and signs_ontology.json.
  * `_SEXED_SUFFIX` (build_ontology.py) is dead code with an over-broad second
    alternative; left unused, flagged here so it is not silently resurrected.

Run from anywhere:
    pytest tests/test_inventory.py -v
"""
import json
import math
import os
import re
import sys

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
# corpus_info lives in scripts/ and is imported TOP-LEVEL by floor_cleaned
# (which itself puts scripts/ on the path); mirror that so both import styles work.
_SCRIPTS = os.path.join(_REPO_ROOT, "scripts")
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

# import the module under test + the shared floor math (the source of truth)
from scripts.inventory import build_ontology as ont  # noqa: E402
from scripts.inventory.build_ontology import (  # noqa: E402
    classify_token,
    _conservative_id,
    _exploratory_id,
    SYLL_CLASSES,
)
from corpus_info import stats as ci_stats, unicity as ci_unicity  # noqa: E402

import pytest  # noqa: E402

SILVER = os.path.join(_REPO_ROOT, "corpus", "silver")


# --------------------------------------------------------------------------- #
# helpers / fixtures
# --------------------------------------------------------------------------- #
def _load(name):
    with open(os.path.join(SILVER, name)) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def ontology():
    return _load("signs_ontology.json")


@pytest.fixture(scope="module")
def inventories():
    return {
        "raw": _load("inventory_syllabograms_raw.json"),
        "conservative": _load("inventory_syllabograms_conservative.json"),
        "exploratory": _load("inventory_syllabograms_exploratory.json"),
    }


@pytest.fixture(scope="module")
def streams():
    return {
        "raw": _load("inventory_syllabograms_raw.stream.json"),
        "conservative": _load("inventory_syllabograms_conservative.stream.json"),
        "exploratory": _load("inventory_syllabograms_exploratory.stream.json"),
    }


# a token is a syllabogram-stream contaminant if its id carries a logogram /
# numeral / fraction marker, or a known commodity-ideogram fragment.
_LOGO_RE = re.compile(
    r"OLIV|VAS|GRA|VIN|VIR|HIDE|TELA|CYP|CAP|BOS|AROM|GAL|MUL|^OLE|VS"
)


def _is_contaminant(sid):
    if not sid:
        return False
    if sid.startswith(("LOGO:", "NUM:", "FRAC:")):
        return True
    return bool(_LOGO_RE.search(sid))


# --------------------------------------------------------------------------- #
# 1. CLASSIFICATION
# --------------------------------------------------------------------------- #
class TestFunctionalClassComplete:
    def test_every_canonical_sign_has_a_functional_class(self, ontology):
        """Invariant from the brief: no canonical sign is left without a class."""
        missing = [cid for cid, m in ontology.items() if not m.get("class")]
        assert missing == [], f"signs without a functional_class: {missing}"

    def test_functional_class_is_a_known_label(self, ontology):
        allowed = {
            "syllabogram-AB", "syllabogram-Aonly",
            "logogram", "numeral", "fraction", "separator", "uncertain",
        }
        bad = {cid: m["class"] for cid, m in ontology.items()
               if m.get("class") not in allowed}
        assert bad == {}, f"unknown class labels: {bad}"

    def test_ab_signs_are_bare_cv_or_v(self, ontology):
        """AB-series = shared with Linear B with known values; canonical ids are
        bare syllabic strings (A, TA, QE, RA2 ...), never *-prefixed."""
        ab = [cid for cid, m in ontology.items()
              if m["class"] == "syllabogram-AB"]
        assert ab, "expected some AB syllabograms"
        bad = [c for c in ab if c.startswith("*") or c.startswith(("LOGO:", "NUM:", "FRAC:"))]
        assert bad == [], f"AB signs with non-syllabic ids: {bad}"

    @pytest.mark.xfail(
        reason="BUG: `*OLIV` (olive-oil ideogram) is misclassified "
               "syllabogram-Aonly, so its canonical id does not match the "
               "`*<number>` A-only form. Same root cause as the raw-stream "
               "contamination xfail below; fix in _classify_head.",
        strict=True,
    )
    def test_aonly_signs_carry_the_star_prefix(self, ontology):
        """A-only = GORILA/SigLA *-series (undeciphered). Canonical id must be
        `*<number>` (optionally a letter allograft suffix). This is the real
        GORILA/SigLA editorial convention, not a guess."""
        aonly = [cid for cid, m in ontology.items()
                 if m["class"] == "syllabogram-Aonly"]
        assert aonly, "expected some A-only syllabograms"
        bad = [c for c in aonly if not re.match(r"\*\d+[A-Z]*$", c)]
        assert bad == [], f"A-only ids without star-number form: {bad}"

    def test_ab_and_aonly_are_disjoint(self, ontology):
        ab = {cid for cid, m in ontology.items() if m["class"] == "syllabogram-AB"}
        aonly = {cid for cid, m in ontology.items() if m["class"] == "syllabogram-Aonly"}
        assert ab & aonly == set(), "a sign is both AB and A-only"

    def test_ambiguous_tokens_marked_uncertain_not_forced(self):
        """Tokens that cannot be confidently placed are 'uncertain', never
        silently coerced into a syllabogram class (redteam mandate)."""
        for tok in ("[?]", "[ ]", "QA2", ""):
            r = classify_token(tok)
            assert r["functional_class"] == "uncertain", (
                f"{tok!r}: expected 'uncertain', got {r['functional_class']!r}")

    def test_subscripted_allographs_are_distinct_ab_signs(self):
        """RA2/PA3/TA2/PU2 carry distinct Linear-B values (rya/ai/two/...) and
        must NOT be merged into their base in the raw/conservative inventory:
        they are distinct signs, not glyph variants."""
        for tok, cid in (("RA₂", "RA2"), ("PA₃", "PA3"),
                         ("TA₂", "TA2"), ("PU₂", "PU2")):
            r = classify_token(tok)
            assert r["functional_class"] == "syllabogram-AB"
            assert r["canonical_sign_id"] == cid


class TestStreamPurity:
    def test_logograms_numerals_fractions_absent_from_primary(self, streams):
        """The PRIMARY conservative stream must be syllabograms only -- no
        LOGO:/NUM:/FRAC: ids, no commodity-ideogram fragments."""
        bad = sorted({s for s in streams["conservative"]["stream"]
                      if _is_contaminant(s)})
        assert bad == [], f"conservative stream contaminated: {bad}"

    def test_logograms_numerals_fractions_absent_from_exploratory(self, streams):
        bad = sorted({s for s in streams["exploratory"]["stream"]
                      if _is_contaminant(s)})
        assert bad == [], f"exploratory stream contaminated: {bad}"

    @pytest.mark.xfail(
        reason="BUG: `*OLIV` and `*406VAS` (star-prefixed logograms) are "
               "misclassified as syllabogram-Aonly by _classify_head (the "
               "`*`-prefix default branch returns syllabogram-Aonly for any "
               "*<non-numeric, non-FM> token). They leak into the RAW stream "
               "(3 + 2 occurrences). PRIMARY conservative is clean. Fix: in "
               "_classify_head, route `*<letters>` and `*<digits><letters>` "
               "whose letter-tail is a known ideogram head (OLIV/VAS/...) to "
               "'logogram'.",
        strict=True,
    )
    def test_logograms_absent_from_raw_stream_too(self, streams):
        """The raw stream is the uncurated syllabogram mass, but a logogram is
        still NOT a syllabogram -- star-prefixed ideograms must not appear."""
        bad = sorted({s for s in streams["raw"]["stream"]
                      if _is_contaminant(s)})
        assert bad == [], f"raw stream contaminated: {bad}"

    def test_aegean_fraction_ranges_excluded(self, streams):
        """*800-*829 / *900-*906 / *701 are the Aegean fraction series
        (numbers.txt); none may appear in any syllabogram stream."""
        def is_frac_star(s):
            m = re.match(r"\*(\d+)$", s)
            return bool(m) and ont._is_fraction_star(int(m.group(1)))
        for label in ("raw", "conservative", "exploratory"):
            bad = sorted({s for s in streams[label]["stream"] if is_frac_star(s)})
            assert bad == [], f"{label} stream carries fraction *-series: {bad}"


class TestClassificationEdgeCases:
    """Direct unit tests of classify_token on hand-picked tokens."""

    @pytest.mark.parametrize("tok,cls", [
        ("GRA", "logogram"),
        ("VIN", "logogram"),
        ("VIR", "logogram"),
        ("HIDE", "logogram"),
        ("OLE", "logogram"),
        ("*21F", "logogram"),    # sexed ideogram (female)
        ("*22M", "logogram"),    # sexed ideogram (male)
        ("*802", "fraction"),    # Aegean fraction *-series
        ("*906", "fraction"),
        ("*301", "syllabogram-Aonly"),
        ("*34", "syllabogram-Aonly"),
        ("A", "syllabogram-AB"),
        ("TA", "syllabogram-AB"),
        ("QE", "syllabogram-AB"),
        ("RA₂", "syllabogram-AB"),
    ])
    def test_classify(self, tok, cls):
        assert classify_token(tok)["functional_class"] == cls

    def test_ligature_head_determines_channel(self):
        # logogram head -> whole ligature is a logogram, never enters syll stream
        r = classify_token("VIN+RA")
        assert r["functional_class"] == "logogram"
        # syllabogram head -> syllabogram ligature, decomposed downstream
        r = classify_token("TI+*412VAS")
        assert r["functional_class"] == "syllabogram-AB"

    @pytest.mark.xfail(
        reason="BUG: `*OLIV` is an olive-oil ideogram (OLIV is in "
               "LOGOGRAM_HEADS) but the leading `*` routes it through the "
               "A-only branch, so it is misclassified syllabogram-Aonly. "
               "classify_token('*OLIV+TU') likewise returns syllabogram-Aonly.",
        strict=True,
    )
    def test_star_prefixed_logogram_is_logogram(self):
        assert classify_token("*OLIV")["functional_class"] == "logogram"
        assert classify_token("*OLIV+TU")["functional_class"] == "logogram"

    @pytest.mark.xfail(
        reason="BUG: `*406VAS` is a vessel ideogram (*4XX-VS/*4XXVAS family in "
               "syllables.txt) but _classify_head ignores the VAS tail and "
               "returns syllabogram-Aonly.",
        strict=True,
    )
    def test_star_vessel_compound_is_logogram(self):
        assert classify_token("*406VAS")["functional_class"] == "logogram"


# --------------------------------------------------------------------------- #
# 2. NESTING
# --------------------------------------------------------------------------- #
class TestInventoryNesting:
    def test_exploratory_is_subset_of_conservative(self, inventories):
        """exploratory = conservative + aggressive allograph merges, so every
        exploratory id is already a conservative id (literal set containment)."""
        cons = set(inventories["conservative"]["inventory"])
        expl = set(inventories["exploratory"]["inventory"])
        assert expl <= cons, f"exploratory not subset of conservative: {expl - cons}"

    def test_conservative_ids_derive_from_raw_via_merge(self, inventories):
        """Every conservative id is either a raw id or the conservative-merge
        image of a raw id (*131B/*131C -> *131, *28B -> *28). This is the
        meaningful nesting; literal cons-subset-of-raw is FALSE by design
        (merging introduces base ids the raw layer only has as variants)."""
        raw = set(inventories["raw"]["inventory"])
        cons = set(inventories["conservative"]["inventory"])
        images = {_conservative_id(r) for r in raw}
        unaccounted = cons - images
        assert unaccounted == set(), (
            f"conservative ids not derivable from raw: {sorted(unaccounted)}")

    def test_exploratory_ids_derive_from_conservative_via_merge(self, inventories):
        cons = set(inventories["conservative"]["inventory"])
        expl = set(inventories["exploratory"]["inventory"])
        images = {_exploratory_id(c) for c in cons}
        unaccounted = expl - images
        assert unaccounted == set(), (
            f"exploratory ids not derivable from conservative: {sorted(unaccounted)}")

    def test_volume_decreases_raw_ge_cons_ge_expl(self, inventories):
        """V(raw) >= V(conservative) >= V(exploratory): each layer curates down."""
        v = {k: inventories[k]["V"] for k in ("raw", "conservative", "exploratory")}
        assert v["raw"] >= v["conservative"] >= v["exploratory"], v

    def test_literal_cons_subset_of_raw_is_false_by_design(self, inventories):
        """Documents the nesting caveat: literal set-containment raw >= cons
        does NOT hold, because the conservative merge introduces base ids
        (*131, *28) whose raw layer only has the allograph variants (*131B,
        *28B). This is expected merging behaviour, not a bug."""
        raw = set(inventories["raw"]["inventory"])
        cons = set(inventories["conservative"]["inventory"])
        # the only ids in conservative-but-not-raw must be conservative-merge
        # bases (i.e. each has a raw allograph variant that maps to it).
        diff = cons - raw
        for cid in diff:
            variants = [r for r in raw if _conservative_id(r) == cid]
            assert variants, (
                f"conservative id {cid!r} in cons but not raw, and no raw "
                f"allograph merges to it -- genuine nesting break")


# --------------------------------------------------------------------------- #
# 3. FLOOR RECOMPUTE
# --------------------------------------------------------------------------- #
class TestFloorRecompute:
    def _stats_from_stream(self, stream_sidecar):
        seqs = stream_sidecar["sequences"]
        docs = [{"id": i, "site": "", "signs": s} for i, s in enumerate(seqs)]
        return ci_stats(docs)

    def test_floor_uses_corpus_info_formula(self):
        """floor_cleaned must reuse corpus_info.stats/unicity verbatim -- it
        imports them, so the formula identity is structural. Confirm the import
        path resolves to the same callables used here."""
        from scripts.inventory import floor_cleaned as fc
        assert fc._stats_docs is ci_stats
        assert fc.unicity is ci_unicity

    def test_conservative_floor_is_self_consistent(self, streams):
        """D = log2(V) - H_rate, H(K) = V*log2(P), U = H(K)/D -- check the three
        identities hold on the recomputed conservative stream."""
        st = self._stats_from_stream(streams["conservative"])
        V, h_rate, n = st["V"], st["h_rate"], st["n"]
        D = math.log2(V) - h_rate
        assert D > 0, "no measured redundancy -> unicity undefined"
        for P in (30, 60, 90):
            un = ci_unicity(V, h_rate, P)
            assert abs(un["D"] - D) < 1e-9
            assert abs(un["H_K"] - V * math.log2(P)) < 1e-9
            assert abs(un["U"] - un["H_K"] / D) < 1e-6

    def test_conservative_inventory_matches_recompute(self, streams, inventories):
        """Re-running corpus_info.stats over the conservative sidecar must
        reproduce the V/N baked into the inventory file."""
        st = self._stats_from_stream(streams["conservative"])
        assert st["V"] == inventories["conservative"]["V"]
        assert st["n"] == inventories["conservative"]["N"]

    def test_cleaning_changes_the_floor_meaningfully(self, streams):
        """Removing logograms/numerals/fractions is required to move H_rate and
        D. The cleaned (conservative) stream must differ from the contaminated
        raw-silver stream on V, H_rate and D -- if it didn't, the cleaning step
        was a no-op."""
        cleaned = self._stats_from_stream(streams["conservative"])
        docs = [
            {"id": d["id"], "site": d.get("site", ""), "signs": d["signs"]}
            for d in _load("inscriptions.json") if d.get("signs")
        ]
        contaminated = ci_stats(docs)
        # V drops substantially (logograms/numerals removed)
        assert cleaned["V"] < contaminated["V"] - 50
        # H_rate rises: syllabograms are LESS predictable than the logogram /
        # numeral heavy contaminated stream (low-entropy high-freq signs lower
        # conditional entropy), so removing them raises H_rate.
        assert cleaned["h_rate"] > contaminated["h_rate"]
        # D = log2(V) - H_rate falls on both axes (smaller V, larger H_rate).
        D_clean = math.log2(cleaned["V"]) - cleaned["h_rate"]
        D_dirty = math.log2(contaminated["V"]) - contaminated["h_rate"]
        assert D_clean < D_dirty

    def test_toy_verdict_unchanged_direction(self, streams):
        """Both contaminated and cleaned are underdetermined-or-measurable; the
        cleaned U(P=30) must remain a positive finite number below N (the toy
        verdict 'measurable recurrent structure' survives the cleaning)."""
        st = self._stats_from_stream(streams["conservative"])
        un = ci_unicity(st["V"], st["h_rate"], 30)
        assert un["U"] != float("inf")
        assert 0 < un["U"] <= st["n"]
