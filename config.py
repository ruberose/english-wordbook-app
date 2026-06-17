"""앱 설정 저장/불러오기 — AppData\\Roaming\\영어단어장\\config.json"""
import json
from pathlib import Path

APP_NAME = "영어단어장"
XLSX_FILENAME = "english-wordbook.xlsx"


def _config_dir() -> Path:
    d = Path.home() / "AppData" / "Roaming" / APP_NAME
    d.mkdir(parents=True, exist_ok=True)
    return d


def _config_path() -> Path:
    return _config_dir() / "config.json"


def _default_xlsx() -> Path:
    return _config_dir() / XLSX_FILENAME


def load_xlsx_path() -> Path:
    """저장된 xlsx 경로 반환. 없으면 기본 AppData 경로."""
    try:
        data = json.loads(_config_path().read_text(encoding="utf-8"))
        p = Path(data.get("xlsx_path", ""))
        if p.exists():
            return p
    except Exception:
        pass
    return _default_xlsx()


def save_xlsx_path(path: Path) -> None:
    data = {}
    if _config_path().exists():
        try:
            data = json.loads(_config_path().read_text(encoding="utf-8"))
        except Exception:
            pass
    data["xlsx_path"] = str(path)
    _config_path().write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
