#!/usr/bin/env python3
"""Build the 5 sealed-challenge manifests for the Linear A foundry (WP seals).

Each seal is a HELD-OUT partition committed by a sha256 over its canonical held-out payload.
The manifest records: the deterministic split criterion, the held-out identifiers, the
commitment hash, and EXACTLY what a candidate reading would have to predict to be scored.

CRUCIAL honest note preserved in every manifest: NO candidate survived the end-to-end
multi-family null (WP6 agnostic + candidate round 1 both AT_END_TO_END_NULL; West Semitic
'cleared' 0.030 but the random control cleared too -> artifact). There is therefore NO
candidate to TEST against these seals right now. Each seal is recorded with status
``NO_CANDIDATE_TO_SEAL`` and its manifest is preserved for any FUTURE candidate. This
documents the blocker per the mandate; it does not manufacture a reading.

Deterministic: SEED=20260708. Read-only corpus. Writes manifests/ and data/ only.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import random

import seal_common as C

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
MANI = os.path.join(ROOT, "manifests")
os.makedirs(DATA, exist_ok=True)
os.makedirs(MANI, exist_ok=True)

AS_OF = "2026-07-07"
STATUS = "NO_CANDIDATE_TO_SEAL"

BLOCKER = (
    "No candidate survived the end-to-end multi-family null. WP6 agnostic search and "
    "candidate round 1 were both AT_END_TO_END_NULL under the multi-family null "
    "(order-shuffle + wrong-language opaque LB + random-prior). West Semitic 'cleared' at "
    "0.030 but the random-prior control also cleared -> artifact, not signal. There is no "
    "surviving candidate to score against this seal. The manifest is committed and preserved "
    "so any FUTURE candidate is scored on a partition it could not have seen."
)


def dump(path, obj):
    with open(path, "w") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
    return path


def main():
    recs = C.load_inscriptions()
    keep = C.conservative_inventory()
    by_id = {r["id"]: r for r in recs}
    all_ids = sorted(by_id)

    # word-unit counts per inscription (syllabic, conservative inventory, >=2 signs =
    # the discriminating units a lexical candidate must read)
    def multi_word_count(rec):
        return sum(1 for w in C.a_word_units(rec, keep) if len(w) >= 2)

    seals = []

    # ---------------------------------------------------------------- SEAL_1
    # Unseen inscriptions: random 15% of all LA inscriptions held out by id.
    rng = random.Random(C.SEED + 1)
    shuffled = all_ids[:]
    rng.shuffle(shuffled)
    n_hold = round(0.15 * len(all_ids))
    s1_ids = sorted(shuffled[:n_hold])
    s1_words = sum(multi_word_count(by_id[i]) for i in s1_ids)
    s1_payload = {"held_out_inscription_ids": s1_ids}
    s1_hash = C.sha256_canonical(s1_payload)
    dump(os.path.join(DATA, "seal_1_heldout.json"), s1_payload)
    seals.append({
        "seal_id": "SEAL_1",
        "name": "unseen_inscriptions",
        "type": "held_out_inscriptions_random",
        "split_criterion": (
            f"Deterministic random 15% of all {len(all_ids)} LA inscriptions, held out by id. "
            f"random.Random(SEED+1) shuffle of the sorted id list; first {n_hold} taken."
        ),
        "seed": C.SEED + 1,
        "n_held_out_inscriptions": len(s1_ids),
        "n_held_out_multisign_words": s1_words,
        "held_out_ids_file": "data/seal_1_heldout.json",
        "commitment_sha256": s1_hash,
        "candidate_must_predict": (
            "For each held-out inscription's multi-sign syllabic word units, a committed "
            "phonetic/lexical reading (value string and, where claimed, gloss). Scored as "
            "token-weighted held-out match rate vs the WP6 multi-family null (order-shuffle, "
            "wrong-language opaque LB, random-prior). CLEARS only if Holm-adjusted decisive "
            "FWER < 0.05 AND leave-one-lexeme-out stays < 0.05."
        ),
    })

    # ---------------------------------------------------------------- SEAL_2
    # Unseen site: the LARGEST non-Haghia-Triada site held out whole.
    from collections import Counter
    site_counts = Counter(r["site"] for r in recs if r["site"] and r["site"] != "Haghia Triada")
    chosen_site = max(sorted(site_counts), key=lambda s: site_counts[s])  # deterministic
    s2_ids = sorted(r["id"] for r in recs if r["site"] == chosen_site)
    s2_words = sum(multi_word_count(by_id[i]) for i in s2_ids)
    s2_payload = {"held_out_site": chosen_site, "held_out_inscription_ids": s2_ids}
    s2_hash = C.sha256_canonical(s2_payload)
    dump(os.path.join(DATA, "seal_2_heldout.json"), s2_payload)
    seals.append({
        "seal_id": "SEAL_2",
        "name": "unseen_site",
        "type": "held_out_whole_site",
        "split_criterion": (
            f"The largest non-Haghia-Triada site by inscription count, held out whole = "
            f"'{chosen_site}' ({len(s2_ids)} inscriptions). A distinct scribal tradition the "
            f"candidate never trained on; tests site-transfer, not memorization."
        ),
        "seed": C.SEED,
        "held_out_site": chosen_site,
        "n_held_out_inscriptions": len(s2_ids),
        "n_held_out_multisign_words": s2_words,
        "held_out_ids_file": "data/seal_2_heldout.json",
        "commitment_sha256": s2_hash,
        "candidate_must_predict": (
            f"Readings for the multi-sign syllabic word units of every '{chosen_site}' "
            "inscription. The correspondence must be fixed BEFORE seeing this site. Scored as "
            "token-weighted held-out match rate vs the multi-family null; site-transfer means "
            "the reading must not degrade to chance off Haghia Triada."
        ),
    })

    # ---------------------------------------------------------------- SEAL_3
    # Unseen formula family: the libation-formula carriers held out whole.
    carriers = {r["id"]: C.is_libation_carrier(r) for r in recs}
    s3_ids = sorted(i for i, f in carriers.items() if f)
    s3_words = sum(multi_word_count(by_id[i]) for i in s3_ids)
    s3_payload = {
        "held_out_inscription_ids": s3_ids,
        "formula_heads_per_id": {i: carriers[i] for i in s3_ids},
        "criterion_formula_words": ["-".join(w) for w in C.LIBATION_FORMULA_WORDS],
    }
    s3_hash = C.sha256_canonical(s3_payload)
    dump(os.path.join(DATA, "seal_3_heldout.json"), s3_payload)
    seals.append({
        "seal_id": "SEAL_3",
        "name": "unseen_formula_family",
        "type": "held_out_libation_formula_carriers",
        "split_criterion": (
            "Every inscription carrying a canonical Linear A libation-formula word (whole word "
            "or head match) held out whole. Fixed published formula list (Duhoux/Davis/Consani): "
            + ", ".join("-".join(w) for w in C.LIBATION_FORMULA_WORDS) + "."
        ),
        "seed": C.SEED,
        "n_held_out_inscriptions": len(s3_ids),
        "n_held_out_multisign_words": s3_words,
        "held_out_ids_file": "data/seal_3_heldout.json",
        "commitment_sha256": s3_hash,
        "candidate_must_predict": (
            "The recurrent libation-formula words (JA-SA-SA-RA-ME, A-TA-I-*301-WA-JA, "
            "U-NA-KA-NA-SI, I-PI-NA-MA, SI-RU-TE, ...) form a religious register absent from the "
            "Haghia-Triada administrative corpus. A candidate must give a coherent, held-out "
            "reading of these formula words as a unit (a plausible libation/dedication semantics), "
            "not an admin-fit. This is the hardest genre-transfer seal."
        ),
    })

    # ---------------------------------------------------------------- SEAL_4
    # Masked-notation reconstruction: hold out a random 15% of ALL numeral tokens.
    rng4 = random.Random(C.SEED + 4)
    all_nums = []
    for i in all_ids:
        for nt in C.numeral_tokens(by_id[i]):
            all_nums.append({"id": i, "stream_index": nt["stream_index"], "value": nt["value"]})
    all_nums.sort(key=lambda d: (d["id"], d["stream_index"]))
    idx = list(range(len(all_nums)))
    rng4.shuffle(idx)
    k = round(0.15 * len(all_nums))
    masked = sorted((all_nums[j] for j in idx[:k]), key=lambda d: (d["id"], d["stream_index"]))
    s4_payload = {"masked_numeral_tokens": masked}
    s4_hash = C.sha256_canonical(s4_payload)
    dump(os.path.join(DATA, "seal_4_heldout.json"), s4_payload)
    n_ins4 = len({m["id"] for m in masked})
    seals.append({
        "seal_id": "SEAL_4",
        "name": "masked_notation_reconstruction",
        "type": "held_out_numeral_positions",
        "split_criterion": (
            f"A deterministic random 15% of all {len(all_nums)} numeral tokens in the corpus "
            f"({k} tokens across {n_ins4} inscriptions) masked at their stream positions. "
            f"random.Random(SEED+4) shuffle of the sorted (id,stream_index) numeral list."
        ),
        "seed": C.SEED + 4,
        "n_masked_numerals": k,
        "n_inscriptions_touched": n_ins4,
        "held_out_ids_file": "data/seal_4_heldout.json",
        "commitment_sha256": s4_hash,
        "candidate_must_predict": (
            "For each masked position, the numeric value (and, where a reading implies it, the "
            "commodity logogram / accounting role the number attaches to). A metrological or "
            "accounting model of the tablets must reconstruct the masked quantities from the "
            "surrounding word context. Scored as exact/within-tolerance value recovery vs a "
            "position-and-margin-total baseline; a reading that constrains totals (KU-RO/KI-RO "
            "sum semantics) predicts these non-trivially."
        ),
    })

    # ---------------------------------------------------------------- SEAL_5
    # PROSPECTIVE gold: Anetaki II, forthcoming INSTAP editio princeps. Not in the corpus yet.
    s5_reg = {
        "inscription": "Anetaki II",
        "designation": "KN Zg 57/58",
        "approx_sign_count": 119,
        "publication": "forthcoming INSTAP editio princeps (editio princeps not yet public)",
        "registered_as_of": AS_OF,
        "in_current_corpus": False,
        "note": (
            "A large (~119-sign) newly-read inscription NOT in the silver corpus. This is the "
            "Linear-B-new-tablet standard: a genuinely prospective target. The reading "
            "correspondence must be frozen and hash-committed NOW; when the editio princeps "
            "publishes, the frozen candidate is applied blind and scored. No part of Anetaki II "
            "informs any candidate formation before publication (strict PIT / as_of gate)."
        ),
    }
    s5_hash = C.sha256_canonical(s5_reg)
    dump(os.path.join(DATA, "seal_5_prospective_registration.json"), s5_reg)
    seals.append({
        "seal_id": "SEAL_5",
        "name": "prospective_gold_anetaki_II",
        "type": "prospective_pre_registration",
        "split_criterion": (
            "Dated pre-registration of a forthcoming inscription NOT in the current corpus: "
            "Anetaki II (KN Zg 57/58, ~119 signs, forthcoming INSTAP editio princeps). Scored "
            "only when it publishes; strictly held out by time (as_of=" + AS_OF + ")."
        ),
        "seed": C.SEED,
        "registered_as_of": AS_OF,
        "in_current_corpus": False,
        "registration_file": "data/seal_5_prospective_registration.json",
        "commitment_sha256": s5_hash,
        "candidate_must_predict": (
            "A frozen phonetic/lexical reading applied blind to Anetaki II's word units on "
            "publication: predicted values/glosses for its multi-sign words, and any structural "
            "prediction (names, formula membership, admin vs cult register). This is the "
            "gold-standard prospective test -- the strongest possible held-out evidence."
        ),
    })

    # ---------------------------------------------------------------- write manifests
    written = []
    for s in seals:
        s["status"] = STATUS
        s["blocker"] = BLOCKER
        s["registered_before_any_candidate"] = True
        s["non_circular"] = (
            "The split is defined by public metadata (id / site / published formula list / "
            "numeral positions / a forthcoming publication), never by any candidate's fit. The "
            "held-out payload is committed by commitment_sha256 so it cannot be altered post hoc."
        )
        fname = f"{s['seal_id']}_{s['name']}.json"
        dump(os.path.join(MANI, fname), s)
        written.append(fname)

    index = {
        "schema": "foundry.seals_index/v1",
        "programme": "sealed-challenge prediction programme (WP seals)",
        "seed": C.SEED,
        "built_as_of": AS_OF,
        "n_inscriptions_total": len(all_ids),
        "overall_status": STATUS,
        "overall_note": (
            "5 sealed held-out challenges committed. Per the mandate, NO candidate currently "
            "exists to test against them (WP6 + candidate rounds all AT_END_TO_END_NULL). Each "
            "manifest is preserved for any future candidate; scoring is deferred until a "
            "candidate survives the end-to-end multi-family null."
        ),
        "seals": [
            {
                "seal_id": s["seal_id"],
                "name": s["name"],
                "manifest": f"manifests/{s['seal_id']}_{s['name']}.json",
                "commitment_sha256": s["commitment_sha256"],
                "n_held_out_inscriptions": s.get("n_held_out_inscriptions"),
                "status": s["status"],
            }
            for s in seals
        ],
    }
    dump(os.path.join(MANI, "SEALS_INDEX.json"), index)

    print("SEALED-CHALLENGE MANIFESTS BUILT (status=%s)" % STATUS)
    for s in seals:
        print(f"  {s['seal_id']:7s} {s['name']:34s} "
              f"n_ins={str(s.get('n_held_out_inscriptions','-')):>4s}  "
              f"sha256={s['commitment_sha256'][:16]}...")
    print("index: manifests/SEALS_INDEX.json")


if __name__ == "__main__":
    main()
