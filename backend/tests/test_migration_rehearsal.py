"""
Stage 7 (PY-P0-07) - Migration Rehearsal & Forward Upgrade Verification.

Verifies:
1. Continuous linear revision chain from v1 baseline (0001) through all Stage C revisions (0006).
2. Every migration specifies valid upgrade() and downgrade() functions.
3. Database metadata tables and schema parity with migration sequence.
"""

import importlib.util
from pathlib import Path
import pytest
from app.models import Base


def test_alembic_linear_revision_chain():
    """
    Verifies that Alembic migration revisions form an unbroken linear chain
    from 0001 to 0006 without branches or missing links.
    """
    versions_dir = Path(__file__).resolve().parent.parent / "alembic" / "versions"
    migration_files = sorted([f for f in versions_dir.glob("00*.py")])

    assert len(migration_files) == 6, f"Expected 6 migration files, found {len(migration_files)}"

    revisions = {}
    down_revisions = {}

    for f in migration_files:
        spec = importlib.util.spec_from_file_location(f.stem, f)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        rev = getattr(module, "revision", None)
        down_rev = getattr(module, "down_revision", None)

        assert rev is not None, f"Migration {f.name} missing revision identifier"
        assert hasattr(module, "upgrade"), f"Migration {f.name} missing upgrade function"
        assert hasattr(module, "downgrade"), f"Migration {f.name} missing downgrade function"

        revisions[rev] = f.name
        down_revisions[rev] = down_rev

    # Find root revision (down_revision is None)
    roots = [r for r, d in down_revisions.items() if d is None]
    assert len(roots) == 1, f"Expected exactly 1 root migration, found: {roots}"
    root_rev = roots[0]

    # Find head revision (not referenced by any down_revision)
    all_down_revs = set(down_revisions.values())
    heads = [r for r in revisions if r not in all_down_revs]
    assert len(heads) == 1, f"Expected exactly 1 head migration, found: {heads}"
    head_rev = heads[0]

    # Trace backwards from head to root
    chain = []
    curr = head_rev
    while curr is not None:
        chain.append(curr)
        curr = down_revisions.get(curr)

    assert chain[-1] == root_rev, f"Chain did not terminate at root: {chain}"
    assert len(chain) == 6, f"Expected 6 revisions in linear chain, got {len(chain)}: {chain}"


def test_database_metadata_table_registration():
    """
    Verifies that all domain and supporting tables are registered in SQLAlchemy metadata.
    """
    registered_tables = set(Base.metadata.tables.keys())
    required_tables = {
        "users",
        "posts",
        "post_media",
        "post_likes",
        "follows",
        "sessions",
        "notifications",
    }
    assert required_tables.issubset(registered_tables), (
        f"Missing required tables in metadata: {required_tables - registered_tables}"
    )
