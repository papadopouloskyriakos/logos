"""Locked properties of the divergence register (scripts/divergence_register.py)
and the scoped Younger parser (scripts/younger_parser.py):

(a) designation bridge: the extended sigla_designation() handles EVERY silver support
    class (Wa/Wb/Wc/Wd/Wg/Wy, Za..Zg) and round-trips through silver_id(); it is
    anchored (trailing-junk ids pass through unchanged, never mis-keyed) and agrees
    with the frozen audit_ab21_ab22.sigla_designation() on the forms that one handles;
(b) verdict ladder + fold_family: exact audit semantics as pure functions; the fold
    collapses silver *-forms, SigLA AB-forms and Younger Latin forms; ligatures never
    fold (never positionally adjudicated);
(c) Younger row extraction hazards on synthetic rows: spaced subscript
    (KU-PA 3 -NU -> KU-PA3-NU), hyphen wrap, spaced numeral (9 7 -> 97), gender merge
    (OVIS f -> OVISf), spaced ligature (CAPm + KU), restoration spans, fraction
    letters dropped, prose/commentary never joins a row;
(d) E2E CROSS-VALIDATION: the comparator re-derives the D4 verdict-per-document
    EXACTLY as scripts/audit_ab21_ab22.py prints it (both run, output compared), and
    reproduces the audit doc's pinned counts (35 docs / 49 tokens; AGREE 21,
    INVERTED 11, MIXED 2 = PH(?)31a/b, NOT_IN_SIGLA 1; 11 inverted docs / 15 tokens);
(e) Younger spot checks against >=5 hand-verifiable .txt rows (incl. HT 122 a.8
    KU-RO 31), with the raw-text hazard forms asserted present in the source;
(f) designation bridge round-trips against the REAL SigLA designations for every
    support class attested in both silver and SigLA;
(g) register: the COMMITTED corpus/divergences.json equals a fresh mechanical rebuild
    (no hand edits possible), builds are byte-deterministic, every entry carries
    generated_by, only divergence-carrying docs are excerpted (defect-level policy),
    BR1 carries exactly the 5 bracket-residue labels, D1 mirrors the Phase-1 annex.

Data-dependent tests are licensed_data-marked AND runtime-skipped when the gitignored
bronze/silver are absent (house pattern).
"""
import contextlib
import io
import json
import os
import re
import sys

import pytest

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from scripts import audit_ab21_ab22 as audit          # noqa: E402
from scripts import divergence_register as dr         # noqa: E402
from scripts import younger_parser as yp              # noqa: E402

_have_data = all(os.path.exists(p) for p in (
    dr.SILVER, dr.SIGLA, dr.ANNEX,
    os.path.join(yp.YOUNGER_DIR, "HTtexts.txt"),
    os.path.join(yp.YOUNGER_DIR, "misctexts.txt"),
))
needs_data = pytest.mark.skipif(not _have_data, reason="gitignored bronze/silver not present")


class TestDesignationBridge:
    # one forward case per support class observed in silver ids + the classless forms
    CASES = [
        ("HT136a", "HT 136a"), ("HT20", "HT 20"), ("PH(?)31a", "PH 31a"),
        ("HTWa1001", "HT Wa 1001"), ("HTWb229", "HT Wb 229"), ("KNWc29", "KN Wc 29"),
        ("HTWd1617", "HT Wd 1617"), ("PHWg45", "PH Wg 45"), ("PEWy5", "PE Wy 5"),
        ("IOZa2", "IO Za 2"), ("HTZb158a", "HT Zb 158a"), ("KHZc106", "KH Zc 106"),
        ("HTZd155", "HT Zd 155"), ("KNZe16", "KN Ze 16"), ("HTZf163", "HT Zf 163"),
        ("KNZg55", "KN Zg 55"),
    ]

    def test_forward(self):
        for sid, des in self.CASES:
            assert dr.sigla_designation(sid) == des, sid

    def test_inverse_round_trip(self):
        for sid, des in self.CASES:
            if "(?)" in sid:
                continue  # documented one-way loss of the (?) marker
            assert dr.silver_id(des) == sid
            assert dr.silver_id(dr.sigla_designation(sid)) == sid

    def test_anchored_pass_through(self):
        # ids the bridge cannot parse must NOT mis-key (the old regex's failure mode)
        for sid in ("THEfr.1", "HTZd157+156", "PEWs", "KNZb<27>", "HTWeWc3020"):
            assert dr.sigla_designation(sid) == sid

    def test_parity_with_frozen_audit_bridge(self):
        # on the forms the frozen Wc-only bridge handles, the two must agree
        for sid in ("HT136a", "HT20", "HT7b", "KNWc29", "HTWc3024", "PH(?)31a", "ZA26b"):
            assert dr.sigla_designation(sid) == audit.sigla_designation(sid)


class TestVerdictLadderAndFold:
    def test_ladder(self):
        assert dr.adjudicate(["21"], None) == "NOT_IN_SIGLA"
        assert dr.adjudicate(["21", "21"], ["21"]) == "COUNT_MISMATCH"
        assert dr.adjudicate(["21", "22"], ["21", "22"]) == "AGREE"
        assert dr.adjudicate(["21", "22"], ["22", "21"]) == "INVERTED"
        assert dr.adjudicate(["21", "22"], ["21", "21"]) == "MIXED"

    def test_fold_family_conventions(self):
        assert dr.fold_family("*21M") == "21" and dr.fold_family("*22F") == "22"
        assert dr.fold_family("AB21") == "21" and dr.fold_family("AB22") == "22"
        assert dr.fold_family("OVIS") == "21" and dr.fold_family("OVISf") == "21"
        assert dr.fold_family("CAP") == "22" and dr.fold_family("CAPm") == "22"

    def test_fold_family_ligatures_and_others_none(self):
        for label in ("OVIS+SI", "CAPm+KU", "OLE+OVISf", "GRA", "KU", "*118"):
            assert dr.fold_family(label) is None, label


class TestYoungerRowExtraction:
    def _row(self, text):
        labels, numbers = yp.extract_row(text.split())
        return labels, numbers

    def test_spaced_subscript(self):
        labels, numbers = self._row("KU-PA 3 -NU 1")
        assert [l[1] for l in labels] == ["KU-PA3-NU"] and numbers == [1]

    def test_spaced_subscript_leading_single_sign(self):
        labels, _ = self._row("I -KU-PA 3 -NA-TU-NA-TE")
        assert [l[1] for l in labels] == ["I-KU-PA3-NA-TU-NA-TE"]

    def test_hyphen_wrap(self):
        labels, _ = self._row("PA-TA- ] NE")
        assert [l[1] for l in labels] == ["PA-TA-NE"]

    def test_spaced_numeral(self):
        _, numbers = self._row("PO-TO-KU-RO 9 7")
        assert numbers == [97]

    def test_gender_merge(self):
        labels, numbers = self._row("QA-RE-TO • OVIS f 27")
        assert [(l[0], l[1]) for l in labels] == [("word", "QA-RE-TO"), ("logo", "OVISf")]
        assert numbers == [27]

    def test_spaced_ligature(self):
        labels, _ = self._row("CAPm + KU 1")
        assert [l[1] for l in labels] == ["CAPm+KU"]
        labels, _ = self._row("OVIS +SI {*512} 4")
        assert [l[1] for l in labels] == ["OVIS+SI"]

    def test_restoration_span_flagged(self):
        labels, numbers = self._row("PA-TA-DA [ OVISm ] 1")
        assert [(l[1], l[2]) for l in labels] == [("PA-TA-DA", False), ("OVISm", True)]
        assert numbers == [1]

    def test_edge_damage_brackets_are_not_spans(self):
        labels, numbers = self._row("] OVISf 1 [")
        assert [(l[1], l[2]) for l in labels] == [("OVISf", False)] and numbers == [1]

    def test_fraction_letters_dropped(self):
        labels, numbers = self._row("CAPm F")
        assert [l[1] for l in labels] == ["CAPm"] and numbers == []
        labels, _ = self._row("] TE L3[")
        assert [l[1] for l in labels] == ["TE"]

    def test_braced_standard_numbers_dropped(self):
        labels, numbers = self._row("TELA+KU {*535: 54+81} 2")
        assert [l[1] for l in labels] == ["TELA+KU"] and numbers == [2]

    def test_prose_never_tokenish(self):
        for line in ("the document probably lists places by name",
                     "a.1 (second half of the heading), b.3 should probably be read",
                     "tablet (HM 1366) (GORILA I: 209-209)"):
            assert not yp._tokenish(line)

    def test_row_lines_tokenish(self):
        for line in ("] OVISf 1 [", "KU-PA 3 -NU    1", "• *305 1 [", "CAPm 1",
                     "U-DE-ZA    2 [", "]KI-SA-NE *303 + D {*624}    J"):
            assert yp._tokenish(line), line


@pytest.mark.licensed_data
@needs_data
class TestD4CrossValidation:
    """The comparator and the frozen audit script must derive IDENTICAL D4 output."""

    @pytest.fixture(scope="class")
    def audit_rows(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            assert audit.main() == 0
        lines = buf.getvalue().splitlines()
        rows, counts = {}, {}
        for ln in lines:
            ch = ln.split()
            if len(ch) >= 5 and ch[-1] in ("AGREE", "INVERTED", "MIXED",
                                           "COUNT_MISMATCH", "NOT_IN_SIGLA"):
                rows[ch[0]] = (ch[-3], ch[-2], ch[-1])   # fams, sigla fams, verdict
        m = re.search(r"tokens in fully-INVERTED documents: (\d+) / (\d+)",
                      buf.getvalue())
        counts["inverted_tokens"], counts["total_tokens"] = int(m.group(1)), int(m.group(2))
        return rows, counts

    @pytest.fixture(scope="class")
    def comparator_rows(self):
        silver, sigla_by_des = dr.load_witnesses()
        return dr.scan_family_inversion(silver, sigla_by_des)

    def test_verdict_per_document_exactly_equal(self, audit_rows, comparator_rows):
        arows, _ = audit_rows
        mine = {}
        for r in comparator_rows:
            fams = ",".join(audit.FAMILY[t] for t in r["silver"])
            sig = ",".join(s[-2:] for s in r["sigla"]) if r["sigla"] else "-"
            mine[r["id"]] = (fams, sig, r["verdict"])
        assert mine == arows

    def test_pinned_audit_doc_counts(self, audit_rows, comparator_rows):
        _, counts = audit_rows
        n_tok = sum(len(r["silver"]) for r in comparator_rows)
        inv = [r for r in comparator_rows if r["verdict"] == "INVERTED"]
        verdicts = {}
        for r in comparator_rows:
            verdicts[r["verdict"]] = verdicts.get(r["verdict"], 0) + 1
        assert len(comparator_rows) == 35 and n_tok == 49 == counts["total_tokens"]
        assert verdicts == {"AGREE": 21, "INVERTED": 11, "MIXED": 2, "NOT_IN_SIGLA": 1}
        assert len(inv) == 11
        assert sum(len(r["silver"]) for r in inv) == 15 == counts["inverted_tokens"]

    def test_inverted_and_mixed_doc_sets(self, comparator_rows):
        inv = sorted(r["id"] for r in comparator_rows if r["verdict"] == "INVERTED")
        assert inv == ["HT132", "HT136a", "HT20", "HT64", "KH6", "KN28a", "KNWc29",
                       "ZA22", "ZA26a", "ZA26b", "ZA9"]
        mixed = sorted(r["id"] for r in comparator_rows if r["verdict"] == "MIXED")
        assert mixed == ["PH(?)31a", "PH(?)31b"]


@pytest.mark.licensed_data
@needs_data
class TestYoungerSpotChecks:
    """>=5 rows hand-verified from the .txt (raw hazard forms asserted in source)."""

    @pytest.fixture(scope="class")
    def ydocs(self):
        return yp.parse_dir()

    @staticmethod
    def _find(ydocs, des, line, **want):
        for r in ydocs[des]["rows"]:
            if r["line"] == line and all(r[k] == v for k, v in want.items()):
                return r
        raise AssertionError(f"{des} {line} row with {want} not found: "
                             f"{[r for r in ydocs[des]['rows'] if r['line'] == line]}")

    def test_ht122_a8_kuro_31(self, ydocs):
        self._find(ydocs, "HT 122", "a.8", words=["KU-RO"], numbers=[31])

    def test_ht122_b6_potokuro_97_spaced_numeral(self, ydocs):
        self._find(ydocs, "HT 122", "b.6", words=["PO-TO-KU-RO"], numbers=[97])
        raw = open(os.path.join(yp.YOUNGER_DIR, "HTtexts.txt"), encoding="utf-8").read()
        assert re.search(r"b\.6 PO-TO-KU-RO\s+9 7", raw)   # the hazard is real

    def test_ht122_a6_kupa3nu_subscript(self, ydocs):
        self._find(ydocs, "HT 122", "a.6", words=["KU-PA3-NU"], numbers=[1])
        raw = open(os.path.join(yp.YOUNGER_DIR, "HTtexts.txt"), encoding="utf-8").read()
        assert "KU-PA 3 -NU" in raw                        # the hazard is real

    def test_ht132_qareto_ovisf_27(self, ydocs):
        self._find(ydocs, "HT 132", ".1-2", words=["QA-RE-TO"],
                   logograms=["OVISf"], numbers=[27])

    def test_ht38_ovis_3(self, ydocs):
        self._find(ydocs, "HT 38", ".2", logograms=["OVIS"], numbers=[3])

    def test_ht64_capm_6(self, ydocs):
        self._find(ydocs, "HT 64", ".4", logograms=["CAPm"], numbers=[6])

    def test_kn28_a2_ovisf_1(self, ydocs):
        self._find(ydocs, "KN 28", "a.2", logograms=["OVISf"], numbers=[1])

    def test_parse_is_deterministic(self, ydocs):
        again = yp.parse_dir()
        assert json.dumps(ydocs, sort_keys=True) == json.dumps(again, sort_keys=True)

    def test_parser_version_pinned_volume(self, ydocs):
        # regression values for younger-parser-v1 (re-pin on intentional parser change)
        assert len(ydocs) == 904
        assert sum(len(d["rows"]) for d in ydocs.values()) == 2191


@pytest.mark.licensed_data
@needs_data
class TestBridgeAgainstRealSigla:
    def test_every_shared_support_class_bridges(self):
        silver, sigla_by_des = dr.load_witnesses()
        hit_classes = set()
        for doc in silver:
            m = dr._ID.match(doc["id"])
            if m and dr.sigla_designation(doc["id"]) in sigla_by_des:
                hit_classes.add(m.group(3))
        # every support class attested in BOTH silver ids and SigLA designations
        assert {"Wa", "Wb", "Wc", "Za", "Zb", "Zc", "Zd", "Ze", "Zf", "Zg"} <= hit_classes
        assert None in hit_classes                        # classless tablets bridge too

    def test_bridged_designations_round_trip(self):
        silver, sigla_by_des = dr.load_witnesses()
        for doc in silver:
            if "(?)" in doc["id"]:
                continue
            des = dr.sigla_designation(doc["id"])
            if des in sigla_by_des and des != doc["id"]:
                assert dr.silver_id(des) == doc["id"]


@pytest.mark.licensed_data
@needs_data
class TestRegister:
    @pytest.fixture(scope="class")
    def built(self):
        register, d4_rows = dr.build_register()
        return register, d4_rows

    def test_committed_file_is_a_fresh_rebuild(self, built):
        register, _ = built
        committed = open(dr.OUT, encoding="utf-8").read()
        assert committed == dr.dumps(register), (
            "corpus/divergences.json differs from a mechanical rebuild — regenerate "
            "with scripts/divergence_register.py, never hand-edit (invariant 12)")

    def test_determinism(self, built):
        register, _ = built
        again, _ = dr.build_register()
        assert dr.dumps(register) == dr.dumps(again)

    def test_every_entry_generated_by(self, built):
        register, _ = built
        assert [e["id"] for e in register["entries"]] == ["D4", "HT38", "D1", "BR1"]
        for e in register["entries"]:
            assert e["generated_by"] == dr.GENERATED_BY
            assert e["status"] == "CONFIRMED"
            for key in ("kind", "docs", "evidence", "sensitive_analyses"):
                assert key in e, (e["id"], key)

    def test_d4_entry_defect_level_only(self, built):
        register, _ = built
        d4 = register["entries"][0]
        assert set(d4["docs"]) == {"HT132", "HT136a", "HT20", "HT64", "KH6", "KN28a",
                                   "KNWc29", "ZA22", "ZA26a", "ZA26b", "ZA9",
                                   "PH(?)31a", "PH(?)31b"}
        for d in d4["docs"].values():
            assert d["verdict"] in ("INVERTED", "MIXED")  # never an AGREE excerpt
        assert d4["evidence"]["inverted_docs"] == 11
        assert d4["evidence"]["tokens_in_inverted_docs"] == 15
        assert d4["evidence"]["per_document_verdicts"] == {
            "AGREE": 21, "INVERTED": 11, "MIXED": 2, "NOT_IN_SIGLA": 1}

    def test_d4_younger_witness_agrees_with_sigla(self, built):
        register, _ = built
        d4 = register["entries"][0]
        for did, d in d4["docs"].items():
            y = d["readings"]["younger"]
            if y is None or d["verdict"] != "INVERTED":
                continue
            assert ({dr.fold_family(l) for l in y}
                    == {s[-2:] for s in d["readings"]["sigla"]}), did

    def test_ht38_entry(self, built):
        register, _ = built
        ht38 = register["entries"][1]
        assert set(ht38["docs"]) == {"HT38", "KHWc2102", "PHWc44"}
        assert ht38["docs"]["HT38"]["readings"] == {
            "silver": ["CAP"], "sigla": ["AB21"], "younger": ["OVIS"]}
        for did in ("KHWc2102", "PHWc44"):
            assert ht38["docs"][did]["verdict"] == "MISSING_IN_SILVER"
            assert ht38["docs"][did]["readings"]["sigla"] == ["AB21"]

    def test_d1_entry_mirrors_annex(self, built):
        register, _ = built
        d1 = register["entries"][2]
        annex = json.load(open(dr.ANNEX, encoding="utf-8"))
        assert d1["evidence"]["summary"] == annex["summary"]
        assert d1["evidence"]["annex_version"] == annex["version"]
        assert d1["evidence"]["bronze_sha256"] == annex["bronze_sha256"]

    def test_br1_exactly_the_five_labels(self, built):
        register, _ = built
        br1 = register["entries"][3]
        assert sorted(br1["docs"]) == ["RO+RO[", "TE+RO[", "WI+ZE[", "]MI+JA", "]TU+RO"]
        assert br1["evidence"]["n_labels"] == 5
        assert br1["evidence"]["n_occurrences"] == 5
        for label, d in br1["docs"].items():
            assert d["implied_clean_label"] == label.strip("[]")

    def test_register_verdicts_match_comparator(self, built):
        register, d4_rows = built
        by_id = {r["id"]: r for r in d4_rows}
        for did, d in register["entries"][0]["docs"].items():
            assert d["verdict"] == by_id[did]["verdict"]
            assert d["readings"]["silver"] == by_id[did]["silver"]
            assert d["readings"]["sigla"] == by_id[did]["sigla"]
