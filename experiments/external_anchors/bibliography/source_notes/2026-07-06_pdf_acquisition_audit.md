# Source acquisition audit — 2026-07-06 (7 PDFs supplied)

PDFs supplied via scp to `/tmp` on nllei01claude01. Copyrighted scans are stored **local-only** in
`data/bronze/pdf_local/` (gitignored; never committed/redistributed); only derived factual records,
citations, and checksums are tracked. Checksums in `data/manifests/acquired_sources.sha256`.

## Mapping to material requests

| PDF | identified as | request | verdict |
|---|---|---|---|
| `dokumen.pub_semitic-words-in-egyptian-texts-…9781400863884.pdf` (594 pp) | **Hoch, *Semitic Words in Egyptian Texts of the New Kingdom and Third Intermediate Period*** (Princeton) | **REQ-02** | **SATISFIED** — the Egyptian foreign-name/group-writing calibration corpus. Unblocks freezing the Egyptian→foreign correspondence model (RQ2/RQ3 pacing item). |
| `Cline2011-SailingGreatGreenSea.pdf` (11 pp) + `Sailing_the_Great_Green_Sea_Amenhotep_II.pdf` (12 pp) | **Cline & Stannish 2011**, JAEI 3.2 — Kom el-Hetan Aegean list (two copies of the same paper) | **REQ-01** | **SUBSTANTIALLY SATISFIED** — reproduces the Egyptian group-writing **transliterations** of the toponyms + IDs + Linear B comparanda + Edel/Görg caveats. Downgrades REQ-01 from BLOCKING → USEFUL (full Edel & Görg apparatus still ideal, no longer gating). |
| `Mari_and_the_Minoans.pdf` (1 p, **image-only**, 1 extractable char) | Mari/Minoans note — **needs OCR**; single page, likely a fragment | **REQ-04** | **PARTIAL** — image stub; REQ-04 stays open for the actual ARM Kaptara texts. |
| `The_Map_Is_Not_the_Territory_Kyriakos_Papadopoulos.pdf` (3 pp) · `The_Map_Is_Not_the_Territory.pdf` (2 pp) | **author's own essay** (K. Papadopoulos, on the agentic system) | — | **not a source** — set aside. |
| `Ο ΚΑΘΡΕΠΤΗΣ.pdf` ("The Mirror", 75 pp, author `spgik`, Greek) | Greek literary/personal work | — | **not a decipherment source** — set aside (not ingested). |

## Derived factual records — Kom el-Hetan toponym forms (from Cline & Stannish 2011, p. ~240, citing Edel & Görg 2005)

The Aegean-list block gives three securely-read Cretan toponyms in Egyptian group writing:

| Egyptian (short) | group-writing transliteration | identification | Linear B comparandum |
|---|---|---|---|
| `knS` | `kA-n-yw-SA` | **Knossos** | ko-no-so |
| `imnS` | `i-m-n-y-SA` | **Amnisos** (a 2nd occurrence on the base) | a-mi-ni-so |
| `rkt` | `ry-kA-ti` | **Lyktos** | (— ) |
| (tentative) | — | **Siteia** (damaged oval) | — |

Also discussed: earlier readings `Amnisa`/`Kunusa`; Edel & Görg's estimated final ovals tentatively
**Phaistos** (pa-i-to) and **Kydonia** (ku-do-ni-ja), which replaced Pisaia / a 2nd Amyklai — **more
contested** (recarving; Edel & Görg tables 191, 213). → Knossos/Amnisos/Lyktos = high-confidence
targets; Siteia/Phaistos/Kydonia = lower-confidence / held-out sensitivity.

**Caveat carried forward:** these transliterations are Cline's rendering of Edel & Görg's readings;
the group-writing→phoneme mapping (e.g., `SA` for /s/-final, `kA`/`ry` vocalization) is exactly what
the **frozen Hoch-calibrated correspondence model** must adjudicate — do NOT hand-map them now.

## Consequence
Both BLOCKING requests cleared. Stage 2 can now build (a) the **Egyptian foreign-name calibration
corpus** from Hoch and (b) the **toponym anchor target set** from Cline — enabling E1 (power) and E2
(Linear-B positive control) design without further acquisition. REQ-04 (Mari) and REQ-03 (EA5647)
remain open but are not on the RQ2 critical path.
