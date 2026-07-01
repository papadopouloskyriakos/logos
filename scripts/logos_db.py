#!/usr/bin/env python3
"""logos DB connector — the single sanctioned factory for the logos MariaDB connection.

Mirrors `../finops-agora/scripts/agora_lib.py` (load_env + db, autocommit, host from .env —
never hardcoded). Every scripts/ module that touches the DB goes through `logos_db.db()` so the
connection shape lives in exactly one place (the finops dedup lesson).

The runner has no mysql client and ProxySQL's cert is untrusted from lab hosts, so the live DB is
reached directly on the Galera member named in `LOGOS_DB_HOST` (same convention as the schema
apply note in schema/schema.sql). Confirms a SELECT against the live DB works.

CLI:
    python3 scripts/logos_db.py            # prints VERSION + a one-row SELECT + the 6 core tables
"""
import os
import sys

# make `from scripts import ...` work whether run as a script or imported (cron + pytest).
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

# NB: pymysql is imported lazily inside db() so this module (and the DB-free unit tests that import it
# transitively) can be collected in a checkout without the driver or a .env.

# the canonical comparison-layer tables this scaffold owns / reads.
CORE_TABLES = ("hypotheses", "verdicts", "family_scores", "graduation_state", "signals", "inscriptions")


def load_env(env_path=None):
    """Load KEY=VALUE pairs from the repo .env into a dict (agora_lib.load_env pattern).

    Missing .env returns an EMPTY dict rather than raising, so importing this module (and hence
    collecting the test suite) NEVER requires a .env / a live DB. Configuration is only needed when
    db() is actually called — unit tests that don't touch the DB run in a bare checkout."""
    path = env_path or os.path.join(_REPO, ".env")
    env = {}
    if not os.path.exists(path):
        return env
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    # process-env overrides file (12-factor): CI/containers set LOGOS_DB_* directly.
    for k in ("LOGOS_DB_HOST", "LOGOS_DB_PORT", "LOGOS_DB_USER", "LOGOS_DB_PASS", "LOGOS_DB_NAME"):
        if os.environ.get(k):
            env[k] = os.environ[k]
    return env


ENV = load_env()

_REQUIRED = ("LOGOS_DB_HOST", "LOGOS_DB_USER", "LOGOS_DB_PASS", "LOGOS_DB_NAME")


def db():
    """Return a pymysql connection to the logos DB (autocommit ON, host/port/creds from .env).

    Mirrors agora_lib.db(): autocommit=True so every INSERT/UPDATE is its own transaction (the
    dedup `ON DUPLICATE KEY UPDATE` pattern depends on this). Creds come from LOGOS_DB_* in .env.
    pymysql is imported LAZILY here so a checkout without the driver can still import this module and
    run the DB-free unit tests; the config check raises a clear, actionable error only WHEN called."""
    missing = [k for k in _REQUIRED if not ENV.get(k)]
    if missing:
        raise RuntimeError(
            "logos DB is not configured: missing " + ", ".join(missing) +
            " — copy .env.example to .env and fill LOGOS_DB_*. (DB-free unit tests run without this.)")
    import pymysql  # lazy: unit tests that never call db() don't need the driver installed
    return pymysql.connect(
        host=ENV["LOGOS_DB_HOST"],
        port=int(ENV.get("LOGOS_DB_PORT", "3306")),
        user=ENV["LOGOS_DB_USER"],
        password=ENV["LOGOS_DB_PASS"],
        database=ENV["LOGOS_DB_NAME"],
        autocommit=True,
        charset="utf8mb4",
    )


def confirm():
    """Round-trip a SELECT against the live logos DB. Returns the (version, db, nrows) tuple.

    Used by tests + a CLI smoke check; raises on any connection failure so problems surface early
    rather than mid-verdict-run.
    """
    conn = db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT VERSION(), DATABASE()")
            version, dbname = cur.fetchone()
            cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=%s", (dbname,))
            nrows = cur.fetchone()[0]
        return (version, dbname, nrows)
    finally:
        conn.close()


if __name__ == "__main__":
    v, d, n = confirm()
    print(f"logos DB OK — MariaDB {v}, database {d}, {n} tables.")
    conn = db()
    try:
        with conn.cursor() as cur:
            cur.execute("SHOW TABLES")
            present = {r[0] for r in cur.fetchall()}
    finally:
        conn.close()
    missing = [t for t in CORE_TABLES if t not in present]
    print("core tables:", ", ".join(t for t in CORE_TABLES if t in present))
    if missing:
        print("MISSING:", ", ".join(missing))
        sys.exit(1)
    print("all core comparison-layer tables present.")
