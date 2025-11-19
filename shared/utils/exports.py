'''Export CSV/XLSX (placeholder)'''
# shared/utils/exports.py
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

EXPORT_DIR = Path("project-ops-export")
EXPORT_DIR.mkdir(exist_ok=True)

def export_csv(rows: List[Dict[str, Any]], filename_prefix: str) -> str:
    df = pd.DataFrame(rows)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = EXPORT_DIR / f"{filename_prefix}_{ts}.csv"
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return str(path)
