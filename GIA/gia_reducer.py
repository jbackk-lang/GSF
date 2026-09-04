"""
GIA/gia_reducer.py

Redukuje model do pol sterujacych zgodnie z gia_map.json.

NAPRAWA (ta sesja): (1) domyślna ścieżka do schematu liczona teraz
względem lokalizacji tego pliku, nie względem cwd -- patrz
TIMDR/validator_timdr.py za identyczne uzasadnienie. (2) dodano
`discarded_fields` (pola z modelu, które NIE weszły do redukcji) --
potrzebne, żeby VALIDATOR mógł policzyć wymiar "gia_overload" dla
RISK; wcześniej nic w kodzie nie liczyło tego wymiaru. (3) "commodity_index"
zmienione na "commodities" -- patrz TIMDR/validator_timdr.py za pełne
uzasadnienie ujednolicenia nazewnictwa surowców w trzech schematach.
"""
import json
from pathlib import Path

_DEFAULT_SCHEMA = Path(__file__).parent / "gia_map.json"


def gia_reduce(model, schema_path=None):
    path = Path(schema_path) if schema_path else _DEFAULT_SCHEMA
    with open(path, "r", encoding="utf-8") as f:
        schema = json.load(f)

    core = schema["core_fields"]
    reduced = {field: model[field] for field in core if field in model}
    discarded = [field for field in model if field not in core]

    return {
        "status": "ok",
        "reduced_model": reduced,
        "discarded_fields": discarded,
        "hint": "Model został zredukowany do pól sterujących zgodnie z GIA.",
    }
