import json
from pathlib import Path


def save_json(model, storage_dir: Path, report_id: str | None, fallback_prefix: str) -> Path | None:
    storage_dir.mkdir(parents=True, exist_ok=True)

    if not report_id:
        i = 1
        while (storage_dir / f"{fallback_prefix}{i}.json").exists():
            i += 1
        report_id = f"{fallback_prefix}{i}"

    path = storage_dir / f"{report_id}.json"
    path.write_text(
        json.dumps(model.model_dump(mode="json"), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Rapor kaydedildi: {path}")
    return path
