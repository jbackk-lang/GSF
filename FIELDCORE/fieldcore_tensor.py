"""
FIELDCORE/fieldcore_tensor.py

Tensor wplywow miedzy czterema rynkami: capital, fx, trade,
commodities (patrz fieldcore_map.json).

NAPRAWA/ROZSZERZENIE (ta sesja):
(1) domyślna ścieżka do schematu liczona względem lokalizacji tego
    pliku, nie względem cwd.
(2) DODANO rozbicie wyniku po rynkach (`markets`) -- wcześniej funkcja
    zwracała tylko jedną zbiorczą listę `problems` bez wskazania, KTÓRY
    z czterech rynków ma brakujące dane. Teraz każdy rynek z
    influence_matrix dostaje własny status ("ok"/"missing_data") i
    listę rynków, na które wpływa -- to jest wejście dla wymiaru
    "fieldcore_tension" w RISK (patrz VALIDATOR/validator.py).
"""
import json
from pathlib import Path

_DEFAULT_SCHEMA = Path(__file__).parent / "fieldcore_map.json"


def fieldcore_tensor(data, schema_path=None):
    path = Path(schema_path) if schema_path else _DEFAULT_SCHEMA
    with open(path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    matrix = schema["influence_matrix"]
    markets = {}
    problems = []

    for market, influences in matrix.items():
        present = market in data
        markets[market] = {
            "status": "ok" if present else "missing_data",
            "influences": influences,
        }
        if not present:
            problems.append(
                f"Brakuje pola '{market}' — tensor wpływów jest niekompletny."
            )

    return {
        "status": "ok" if not problems else "warning",
        "tensor": matrix,
        "markets": markets,
        "hint": problems or ["Tensor wpływów jest kompletny i spójny."],
    }
