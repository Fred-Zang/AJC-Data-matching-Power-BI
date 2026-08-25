from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path

from .config import CV_ROOT, REFERENCE_ROOT, RUNTIME_ROOT, SOURCE_EXPORT_ROOT, ensure_runtime_dirs
from .pipeline import process_cv_directory
from .reference import build_references, load_stopwords, load_variants, load_weights
from .sources.consolidation import consolidate_local_exports
from .sources.remote import sync_configured_exports, upload_file_to_onedrive


def _load_reference_bundle(reference_root: Path):
    stopwords = load_stopwords(reference_root / "stopwords.txt")
    variants = load_variants(reference_root / "tag_variants.csv")
    weights = load_weights(reference_root / "token_weights.csv")
    references = build_references(
        reference_root / "training_catalog.csv",
        stopwords=stopwords,
        variants=variants,
        explicit_weights=weights,
    )
    return stopwords, variants, references


def command_demo(reset: bool) -> int:
    if reset and RUNTIME_ROOT.exists():
        for child in RUNTIME_ROOT.iterdir():
            if child.name == ".gitkeep":
                continue
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    ensure_runtime_dirs()

    consolidated = consolidate_local_exports(SOURCE_EXPORT_ROOT, RUNTIME_ROOT / "staging" / "business_events.csv")
    stopwords, variants, references = _load_reference_bundle(REFERENCE_ROOT)
    rows = process_cv_directory(
        CV_ROOT,
        references,
        variants=variants,
        output_dir=RUNTIME_ROOT / "results",
        document_id_mode="name",
        audit_db=RUNTIME_ROOT / "ajc_demo.db",
    )

    print(f"Sources consolidées : {len(consolidated)} lignes")
    print(f"Filières synthétiques : {len(references)}")
    print(f"Résultats de matching : {len(rows)}")
    print(f"Sorties : {RUNTIME_ROOT.resolve()}")
    return 0


def command_match(cv_dir: Path, reference_root: Path, output_dir: Path) -> int:
    stopwords, variants, references = _load_reference_bundle(reference_root)
    rows = process_cv_directory(cv_dir, references, variants=variants, output_dir=output_dir, document_id_mode="hash", audit_db=RUNTIME_ROOT / "ajc_matching.db")
    print(f"Résultats de matching : {len(rows)}")
    return 0


def command_consolidate(source_dir: Path, output: Path) -> int:
    rows = consolidate_local_exports(source_dir, output)
    print(f"Lignes consolidées : {len(rows)}")
    print(f"Sortie : {output}")
    return 0


def command_sync_remote(output_dir: Path) -> int:
    paths = sync_configured_exports(output_dir)
    print(f"Exports téléchargés : {len(paths)}")
    for path in paths:
        print(path)
    return 0


def command_upload(local_path: Path, remote_folder: str) -> int:
    upload_file_to_onedrive(local_path, remote_folder)
    print(f"Fichier envoyé : {local_path.name}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AJC CV Matching — public deterministic POC")
    sub = parser.add_subparsers(dest="command", required=True)

    demo = sub.add_parser("demo", help="Run the complete synthetic demonstration")
    demo.add_argument("--reset", action="store_true", help="Clear generated runtime outputs first")

    match = sub.add_parser("match", help="Match a local CV directory against a local reference")
    match.add_argument("--cv-dir", type=Path, required=True)
    match.add_argument("--reference-root", type=Path, default=REFERENCE_ROOT)
    match.add_argument("--output-dir", type=Path, default=RUNTIME_ROOT / "results")

    consolidate = sub.add_parser("consolidate-sources", help="Normalize the three synthetic source exports")
    consolidate.add_argument("--source-dir", type=Path, default=SOURCE_EXPORT_ROOT)
    consolidate.add_argument("--output", type=Path, default=RUNTIME_ROOT / "staging" / "business_events.csv")

    sync = sub.add_parser("sync-remote", help="Download explicitly configured remote exports")
    sync.add_argument("--output-dir", type=Path, default=RUNTIME_ROOT / "staging" / "remote")

    upload = sub.add_parser("upload-onedrive", help="Upload one local file through Microsoft Graph")
    upload.add_argument("--file", type=Path, required=True)
    upload.add_argument("--remote-folder", default=os.getenv("MS_GRAPH_REMOTE_FOLDER", ""))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "demo":
        return command_demo(args.reset)
    if args.command == "match":
        return command_match(args.cv_dir, args.reference_root, args.output_dir)
    if args.command == "consolidate-sources":
        return command_consolidate(args.source_dir, args.output)
    if args.command == "sync-remote":
        return command_sync_remote(args.output_dir)
    if args.command == "upload-onedrive":
        return command_upload(args.file, args.remote_folder)
    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
