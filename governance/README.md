# governance/

Constitutional home of LOGOS (Article XXIII; repository convention "Constitutions and amendments live
under `governance/`").

| file | what |
|---|---|
| [`CONSTITUTION.md`](./CONSTITUTION.md) | **Authoritative** constitution, **v2.2** (Preamble + Articles I–XXIII + claim/licence matrix + status vocabulary). |
| [`AMENDMENT-001-v1-to-v2.md`](./AMENDMENT-001-v1-to-v2.md) | v1.0 → v2.0 amendment record (owner's audit + the 12 remedies; non-retroactive). |
| [`AMENDMENT-002-v2.0-to-v2.1.md`](./AMENDMENT-002-v2.0-to-v2.1.md) | v2.0 → v2.1 amendment record (precision fixes B1–B8; non-retroactive). |
| [`AMENDMENT-003-v2.1-to-v2.2.md`](./AMENDMENT-003-v2.1-to-v2.2.md) | v2.1 → v2.2 amendment record (corrects B5 tier direction + B6 layer→licence map). |
| [`CONSTITUTION_SELF_AUDIT.md`](./CONSTITUTION_SELF_AUDIT.md) | Adversarial audits (adoption B1–B8 → v2.1; v2.1 review → v2.2 + code hardening). |
| [`RETROACTIVE_COMPLIANCE.md`](./RETROACTIVE_COMPLIANCE.md) | The existing record re-expressed (not re-graded) in v2.0 vocabulary + claim layers + licence states. |
| [`IMPLEMENTATION_BACKLOG.md`](./IMPLEMENTATION_BACKLOG.md) | New machine-readable obligations v2.0 creates (search receipts, information-budget panel, effective_n, …). |
| [`transfer_licences.json`](./transfer_licences.json) | Machine-readable Linear A transfer-licence state (Art. XV). |
| [`assumption_register.json`](./assumption_register.json) | Load-bearing premises, verified + pinned (Art. XVIII). |
| [`source_dependency_graph.json`](./source_dependency_graph.json) | Evidentiary lineages of every source (Art. XI); consumed by `scripts/source_dependency.py` — collapses dependent sources to one vote, feeds effective_n. |

**Precedence:** this directory > `CLAUDE.md`. `CLAUDE.md` carries a condensed pointer for daily work.

**Governing rule:** every hypothesis is guilty until independent held-out evidence proves it innocent;
every claim is capped at its earned layer; the machine — not the proposer — decides; every honest
negative is permanent.
