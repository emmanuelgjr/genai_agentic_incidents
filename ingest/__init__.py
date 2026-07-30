"""``ingest`` is the corpus-source data directory; ``ingest.common`` (this
package's only code module) is the repo's single network chokepoint --
see ingest/common.py and docs/INGESTION_CONDUCT.md.

This file exists only to make ``ingest`` an explicit, ordinary Python
package (so ``from ingest.common import ...`` is unambiguous) rather than
relying on implicit namespace-package behavior. It has no other effect:
``scripts/merge_and_dedupe.py`` still only picks up ``ingest/*.json`` via
its own glob, never ``*.py`` files, so this module is not, and never will
be, treated as a corpus source.
"""
