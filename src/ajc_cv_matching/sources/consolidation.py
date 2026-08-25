from __future__ import annotations

from pathlib import Path

import pandas as pd


SOURCE_SPECS = {
    "beetween": {
        "file": "beetween_export_EXAMPLE.csv",
        "entity_type": "candidate_event",
        "id": "applicant_id",
        "status": "stage",
        "date": "event_date",
    },
    "quest": {
        "file": "quest_export_EXAMPLE.csv",
        "entity_type": "training_session",
        "id": "session_id",
        "status": "status",
        "date": "start_date",
    },
    "nocrm": {
        "file": "nocrm_export_EXAMPLE.csv",
        "entity_type": "sales_lead",
        "id": "lead_id",
        "status": "status",
        "date": "event_date",
    },
}


def consolidate_local_exports(source_dir: Path, output_path: Path) -> list[dict[str, str]]:
    """Normalize three heterogeneous business exports into a BI-friendly event table."""
    frames: list[pd.DataFrame] = []
    for source_name, spec in SOURCE_SPECS.items():
        source = pd.read_csv(source_dir / spec["file"], dtype=str).fillna("")
        normalized = pd.DataFrame(
            {
                "source": source_name,
                "entity_type": spec["entity_type"],
                "external_id": source[spec["id"]].str.strip(),
                "status": source[spec["status"]].str.strip(),
                "event_date": source[spec["date"]].str.strip(),
            }
        )
        frames.append(normalized)

    result = pd.concat(frames, ignore_index=True).sort_values(
        ["event_date", "source", "external_id"], kind="stable"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)
    return result.to_dict(orient="records")
