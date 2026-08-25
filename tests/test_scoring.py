from ajc_cv_matching.scoring import score_tokens


def test_boolean_and_weighted_scores_are_explainable():
    result = score_tokens(
        ["PYTHON", "SQL"],
        ["PYTHON", "SQL", "POWER"],
        {"PYTHON": 3, "SQL": 3, "POWER": 1},
    )
    assert result.boolean_score == 66.67
    assert result.weighted_score == 85.71
    assert result.matched_tokens == ("PYTHON", "SQL")
    assert result.missing_tokens == ("POWER",)
