from pathlib import Path

from ajc_cv_matching.pipeline import process_cv_directory
from ajc_cv_matching.reference import build_references, load_stopwords, load_variants, load_weights
from ajc_cv_matching.sources.consolidation import consolidate_local_exports


ROOT = Path(__file__).resolve().parents[1]


def test_synthetic_demo_end_to_end(tmp_path):
    ref_root = ROOT / "examples" / "reference"
    stopwords = load_stopwords(ref_root / "stopwords.txt")
    variants = load_variants(ref_root / "tag_variants.csv")
    refs = build_references(
        ref_root / "training_catalog.csv",
        stopwords=stopwords,
        variants=variants,
        explicit_weights=load_weights(ref_root / "token_weights.csv"),
    )
    rows = process_cv_directory(ROOT / "examples" / "cv", refs, variants=variants, output_dir=tmp_path / "results", document_id_mode="name", audit_db=tmp_path / "audit.db")
    assert len(rows) == 9
    perfect = [row for row in rows if row["document_id"] == "Candidate_003" and row["pathway_id"] == "DEV-001"][0]
    assert perfect["weighted_score"] == 100.0

    consolidated = consolidate_local_exports(ROOT / "examples" / "source_exports", tmp_path / "business_events.csv")
    assert len(consolidated) == 9
