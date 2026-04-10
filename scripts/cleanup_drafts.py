#!/usr/bin/env python

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
API_ROOT = REPO_ROOT / "apps" / "api"

for path in (str(REPO_ROOT), str(API_ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

from app.core.config import get_settings
from app.core.db import get_session_factory
from app.core.logging import configure_logging
from app.repositories.job_repository import JobRepository
from app.services.draft_cleanup_service import DraftCleanupService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Clean up expired draft jobs.")
    parser.add_argument(
        "--older-than-hours",
        type=int,
        default=48,
        help="Delete drafts with updated_at older than this many hours. Default: 48.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only inspect up to N draft jobs.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually delete matching draft jobs. Without this flag, the script runs in dry-run mode.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    configure_logging()
    get_settings()
    parser = build_parser()
    args = parser.parse_args(argv)

    session = get_session_factory()()
    try:
        result = DraftCleanupService(session, JobRepository()).cleanup_expired_drafts(
            older_than_hours=args.older_than_hours,
            apply=args.apply,
            limit=args.limit,
        )
    finally:
        session.close()

    mode = "apply" if args.apply else "dry-run"
    if not result.matched_items:
        print(f"[cleanup-drafts] mode={mode} older_than_hours={args.older_than_hours} matched=0")
        print("[cleanup-drafts] 无过期 draft。")
        return 0

    print(
        f"[cleanup-drafts] mode={mode} older_than_hours={args.older_than_hours} "
        f"matched={len(result.matched_items)} deleted={result.deleted_count}"
    )
    for item in result.matched_items:
        print(f"- {item.job_id} updated_at={item.updated_at.isoformat()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
