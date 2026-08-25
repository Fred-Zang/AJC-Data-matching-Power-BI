from pathlib import Path

from ajc_cv_matching.reference import build_references, load_stopwords, load_variants, load_weights


ROOT = Path(__file__).resolve().parents[1]


def test_reference_builds_three_synthetic_pathways():
    ref_root = ROOT / "examples" / "reference"
    refs = build_references(
        ref_root / "training_catalog.csv",
        stopwords=load_stopwords(ref_root / "stopwords.txt"),
        variants=load_variants(ref_root / "tag_variants.csv"),
        explicit_weights=load_weights(ref_root / "token_weights.csv"),
    )
    assert set(refs) == {"DATA-001", "DEVOPS-001", "DEV-001"}
    assert "PYTHON" in refs["DATA-001"].tokens
    assert "KUBERNETES" in refs["DEVOPS-001"].tokens
    assert "C++" in refs["DEV-001"].tokens
