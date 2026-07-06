# ADMINISTRATIVE_CHANNEL_ARCHIVE_MANIFEST — immutable

_Machine-readable form: `data/manifests/administrative_channel_closure.{json,sha256}`._

```
final_branch    = research/la-lb-toponym-continuity
final_commit    = acfd19b1246766ad880f7b96e0da86564750dcdc   (final experiment commit; closure appended after)
seed            = 20260706
test_count      = 76 (all passing)
closure_date    = 2026-07-06
resource_summary= light local CPU only; Monte-Carlo nulls/power N=4000/1500 per cell; no fenced/H100 compute
```

## Input manifest hashes (frozen; unchanged)
| artifact | sha256 |
|---|---|
| la_candidate_packet.jsonl | `eb2bb2933daf40c2…` |
| lb_toponym_target_manifest.jsonl | `29e25d4953518320…` |
| ab_sign_equivalence.json | `77de6684a37cd4ef…` |
| known_persistence_pairs.jsonl | `9e832800386a0ef4…` |

## Result artifact hashes (7)
| artifact | sha256 |
|---|---|
| ablations.json | `e12c2c965be26482…` |
| positive_controls.json | `3ac85fdfb67570fb…` |
| nulls.json | `be421c5e016b7afe…` |
| heldout.json | `ae15e31dc4f1d778…` |
| power.json | `16e5d6cbb0e06786…` |
| circularity.json | `97c81a3861053a21…` |
| final_verdict.json | `305e7469986f2a6f…` |

Full 64-char digests: `data/manifests/administrative_channel_closure.sha256`. Any later ritual/drift
work forks from this point and must not modify these artifacts.
