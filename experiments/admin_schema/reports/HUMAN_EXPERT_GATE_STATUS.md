# Human-expert gate status

```
status                 = INCOMPLETE
human_gold_feasibility = INCOMPLETE
blocker                = QUALIFIED_HUMAN_ANNOTATORS_REQUIRED
```

Explicitly:
- **No human annotations currently exist.**
- **No agreement statistic may be calculated** (compare_human_annotations refuses → BLOCKED).
- **No adjudication may occur** (build_adjudication_packet refuses → BLOCKED).
- **No model may be trained.**
- **No Linear A inference is authorized.**

Completed expert files must LATER be placed at:
```
data/human_pilot/completed/annotator_A_completed.csv
data/human_pilot/completed/annotator_B_completed.csv
```
Then: `validate_human_submission` (both VALID) → `compare_human_annotations` (α vs the frozen 0.80/0.667
gate) → `build_adjudication_packet`. Until two GENUINE human submissions exist, the programme is blocked here.
