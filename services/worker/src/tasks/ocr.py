from __future__ import annotations

from pathlib import Path
from typing import Any

try:  # pragma: no cover - optional dependency
    from paddleocr import PaddleOCR  # type: ignore
except ImportError as exc:  # pragma: no cover
    PaddleOCR = None
    OCR_IMPORT_ERROR = exc
else:
    OCR_IMPORT_ERROR = None

ocr_engine = PaddleOCR(use_angle_cls=True, lang="ch") if PaddleOCR else None


from ..celery_app import celery_app


@celery_app.task(name="services.worker.src.tasks.ocr.extract_text")
def extract_text(image_path: str) -> dict[str, Any]:
    path = Path(image_path)
    if not path.exists():
        return {"error": "file_not_found", "text": ""}
    if ocr_engine is None:
        return {"error": "ocr_not_available", "text": "", "detail": str(OCR_IMPORT_ERROR)}
    result = ocr_engine.ocr(str(path), cls=True)
    lines = []
    for block in result:
        for entry in block:
            if entry and len(entry) > 1:
                lines.append(entry[1][0])
    return {"text": "\n".join(lines), "confidence": [entry[1][1] for block in result for entry in block]}
