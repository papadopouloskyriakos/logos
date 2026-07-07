# G3b - Compound Anchor Systems

**Task.** Find compound systems where independent anchors JOINTLY constrain **>=4 signs**, across **>=2 contexts**, drawing on **>=2 evidence channels**.

**Decisive refinement.** Count not just channels but **INDEPENDENT VALUE-BEARING** channels. Per G1 the only value-bearing channel is the toponym external-referent channel; shape-homomorphy and Cypriot-stability **inherit** the LB value (Art. XII circular). A system can hit the >=2-channel bar while every extra channel supplies zero independent value.

Non-circular: LA values label only. Artifacts: `scripts/g3_compound_systems.py` -> `data/anchors_v2/compound_systems.json`. Seed 20260708.

---

## 1. Enumerated systems (measured)

| system | records | signs | contexts | channels | INDEP value channels | loose bar | STRICT bar |
|---|--:|--:|--:|--:|--:|:--:|:--:|
| TOP-FIRM: 6 firm toponym equations | 6 | 17 | 5 | 1 | **1** | fail | **fail** |
| TOP-CORROB-A: Phaistos + se-to-i-ja (share I,TO) | 2 | 5 | 2 | 1 | **1** | fail | **fail** |
| TOP-CORROB-B: Sybrita + Tylissos (share RI) | 3 | 10 | 2 | 1 | **1** | fail | **fail** |
| HUB-SA: every anchor touching sign SA (all channels) | 10 | 14 | 10 | 5 | **1** | PASS | **fail** |
| CROSS-3CH: firm toponyms + shape + Cypriot on the same signs | 30 | 17 | 30 | 3 | **1** | PASS | **fail** |

Channels present per system (H_shape / C_cypriot INHERIT value; only L_toponym is value-bearing):

- **TOP-FIRM: 6 firm toponym equations**: signs [A,DI,I,JA,KI,PA,RI,RU,SA,SE,SI,SU,TA,TE,TI,TO,TU]; channels [L_toponym]; value-bearing channel TYPES present ['L_toponym']; distinct value referents within channel ['Mt-Dikte', 'Phaistos', 'Sybrita', 'Tylissos', 'se-to-i-ja'].
- **TOP-CORROB-A: Phaistos + se-to-i-ja (share I,TO)**: signs [I,JA,PA,SE,TO]; channels [L_toponym]; value-bearing channel TYPES present ['L_toponym']; distinct value referents within channel ['Phaistos', 'se-to-i-ja'].
- **TOP-CORROB-B: Sybrita + Tylissos (share RI)**: signs [A,KI,RI,RU,SA,SI,SU,TA,TI,TU]; channels [L_toponym]; value-bearing channel TYPES present ['L_toponym']; distinct value referents within channel ['Sybrita', 'Tylissos'].
- **HUB-SA: every anchor touching sign SA (all channels)**: signs [A,I,KA,MA,NA,NI,RA2,RE,RO,RU,SA,SI,TI,TU]; channels [C_cypriot,H_shape,L_personal_name,L_toponym,L_variation_constraint]; value-bearing channel TYPES present ['L_toponym']; distinct value referents within channel ['Tylissos'].
- **CROSS-3CH: firm toponyms + shape + Cypriot on the same signs**: signs [A,DI,I,JA,KI,PA,RI,RU,SA,SE,SI,SU,TA,TE,TI,TO,TU]; channels [C_cypriot,H_shape,L_toponym]; value-bearing channel TYPES present ['L_toponym']; distinct value referents within channel ['Mt-Dikte', 'Phaistos', 'Sybrita', 'Tylissos', 'se-to-i-ja'].

## 2. Richest signs by channel count

| sign | #channels | channels |
|---|--:|---|
| SA | 5 | C_cypriot, H_shape, L_personal_name, L_toponym, L_variation_constraint |
| NA | 5 | C_cypriot, H_shape, L_gloss_acrophonic, L_personal_name, L_toponym |
| PA | 4 | C_cypriot, H_shape, L_personal_name, L_toponym |
| I | 4 | C_cypriot, H_shape, L_personal_name, L_toponym |
| RU | 4 | H_shape, L_gloss_acrophonic, L_personal_name, L_toponym |
| KI | 4 | H_shape, L_gloss_acrophonic, L_personal_name, L_toponym |
| TE | 4 | H_shape, L_personal_name, L_toponym, L_variation_constraint |
| TA | 4 | H_shape, L_personal_name, L_toponym, L_variation_constraint |

A high channel count here is a MULTIPLICITY illusion, not corroboration: the extra channels (H_shape, C_cypriot, L_personal_name) inherit or assert no value, so a sign 'touched by 4 channels' is still pinned by at most one value-bearing referent.

## 3. Headline

- Systems clearing the **loose** bar (>=4 signs, >=2 contexts, >=2 evidence channels): **2** (HUB-SA: every anchor touching sign SA (all channels); CROSS-3CH: firm toponyms + shape + Cypriot on the same signs).

- Systems clearing the **STRICT** bar (>=4 signs, >=2 contexts, >=2 **INDEPENDENT VALUE-BEARING** channels): **0** (NONE).

- Max independent value-bearing channel TYPES reachable by any system: **1** (the toponym channel; no second value-bearing type exists).

- Max distinct firm value referents co-occurring within that one channel: **5** -- apparent within-channel corroboration, but the cited LOTO gate collapses it to {I,RI}, each one-toponym-deep.

Compound systems that reach >=2 EVIDENCE channels exist (e.g. HUB-SA spans 5 channels; CROSS-3CH spans 3), but EVERY system reaches the >=2-channel bar only by adding value-INHERITING channels (shape-homomorphy, Cypriot, personal-name). The number of INDEPENDENT value-bearing channel TYPES in any system is at most 1 (the toponym channel; there is no second value-bearing channel type). Within that one channel, up to 5 distinct firm referents co-occur and can share a sign (apparent corroboration), but the cited frozen LOTO gate collapses even that to {I,RI}, each one-toponym-deep. So NO compound system has >=2 genuinely INDEPENDENT value-bearing channels: the entire value substrate is one channel.

**Consequence.** The campaign's 'no single decisive anchor / >=2 independent symmetry-breaking channels' candidate-ready criterion is **NOT met on the value axis**: the entire value substrate is one channel (toponyms). Compound systems are real and useful for RELATIVE structure (many signs co-constrained across contexts), but they cannot manufacture a second independent value channel out of value-inheriting evidence.

*Generated by `scripts/g3_compound_systems.py`; counts echoed from `data/anchors_v2/compound_systems.json` (invariant 12).*