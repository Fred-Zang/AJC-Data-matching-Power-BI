from ajc_cv_matching.normalization import normalize_text, tokenize


def test_preserves_technical_tokens():
    text = normalize_text("C ++, C#, .NET et Python")
    assert "C++" in text
    assert "C#" in text
    assert ".NET" in text
    assert "PYTHON" in text


def test_variants_are_canonicalized():
    doc = tokenize("K8s GitLab Python3", variants={"K8S": "KUBERNETES", "GITLAB": "GIT", "PYTHON3": "PYTHON"})
    assert set(doc.tokens) == {"KUBERNETES", "GIT", "PYTHON"}
