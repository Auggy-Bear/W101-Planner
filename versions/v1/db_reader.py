"""Read item rows from a single SQLite DB or a directory of `.db.gz` parts."""
from __future__ import annotations

import gzip
import os
import shutil
import sqlite3
import tempfile
from pathlib import Path

QUERY = 'SELECT name, item_type, school, level, props FROM items'


def iter_item_rows(db_path):
    """Yield (name, item_type, school, level, props) from a DB or split parts."""
    path = Path(db_path)
    if not path.exists():
        raise FileNotFoundError(path)

    if path.is_file():
        conn = sqlite3.connect(path)
        try:
            yield from conn.execute(QUERY)
        finally:
            conn.close()
        return

    parts = sorted(path.glob('*.db.gz'))
    if not parts:
        raise FileNotFoundError(f'no .db.gz parts in {path}')

    for part in parts:
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            temp_path = tmp.name
        try:
            with gzip.open(part, 'rb') as src, open(temp_path, 'wb') as dst:
                shutil.copyfileobj(src, dst)
            conn = sqlite3.connect(temp_path)
            try:
                yield from conn.execute(QUERY)
            finally:
                conn.close()
        finally:
            os.unlink(temp_path)
