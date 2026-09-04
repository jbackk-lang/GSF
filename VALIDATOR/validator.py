"""
VALIDATOR/validator.py

Spina TIMDR + GIA + FIELDCORE + core_nodes + RISK w jedną walidację
struktury pola GSF.

NAPRAWIONE (ta sesja):
1. Import `from GSF.CORE-NODES.core_nodes import ...` byl SyntaxErrorem
   (mysnik w nazwie pakietu) -- ten plik nigdy nie mogl sie uruchomic.
   Teraz importuje z GSF.core_nodes (patrz core_nodes/core_nodes.py).
2. RISK nie byl w ogole podlaczony: `analyze_risk()` oczekuje kluczy
   timdr_breaks/gia_overload/fieldcore_tension/core_nodes_weakness
   (z RISK/risk_map.json), a nic wczesniej nie budowalo takiego
   slownika -- validate_gsf() zwracal timdr/gia/fieldcore/nodes i na
   tym sie konczylo, RISK nigdy nie byl wolany. Teraz `structure_report`
   jest budowany z poprawnymi kluczami i przekazywany do analyze_risk().
3. README obiecywal ocene "stabilne/napiete/krytyczne"
   (risk_map.json["levels"]), ale zaden kod jej nie liczyl. Dodano pole
   "level" -- patrz UWAGA O ZAKRESIE ponizej za dokladny (celowo
   uproszczony) sposob liczenia.

DODANE (ta sesja, na prosbe uzytkownika): rozbicie wyniku po rynkach
(capital/fx/trade/commodities) -- patrz FIELDCORE/fieldcore_tensor.py
(`markets`) i pole "fieldcore_tension" ponizej, ktore teraz jest
SLOWNIKIEM per rynek, nie jedna zbiorcza wartoscia.

UWAGA O ZAKRESIE (poziom stable/stressed/critical): liczony tylko z
DWOCH wymiarow, ktore faktycznie zaleza od przekazanych `data` --
timdr_breaks (brakujace pola ciaglosci) i fieldcore_tension (brakujace
rynki). gia_overload i core_nodes_weakness sa tu INFORMACYJNE, nie
wchodza do poziomu: gia_overload mowi tylko, ile pol model ma poza
core_fields (to nie jest samo w sobie "problem"), a core_nodes_weakness
jest STALA per wezel (zdefiniowana raz w core_nodes/nodes.json,
niezalezna od przekazanych `data`) -- wiec nie niesie sygnalu o
BIEZACYM ryzyku. To jest jawne, udokumentowane uproszczenie, nie
ukryta luka -- rozszerzenie o te dwa wymiary wymagaloby decyzji
modelowej (np. prog liczby odrzuconych pol dla gia_overload), ktora
nie zostala tu podjeta.
"""
import json

from GSF.TIMDR.validator_timdr import validate_timdr_continuity
from GSF.GIA.gia_reducer import gia_reduce
from GSF.FIELDCORE.fieldcore_tensor import fieldcore_tensor
from GSF.core_nodes.core_nodes import load_core_nodes, analyze_node
from GSF.RISK.risk_analyzer import analyze_risk

_LEVELS = ["stable", "stressed", "critical"]


def validate_gsf(data):
    timdr = validate_timdr_continuity(data)
    gia = gia_reduce(data)
    field = fieldcore_tensor(data)
    nodes = load_core_nodes()

    node_analysis = {name: analyze_node(nodes["nodes"][name]) for name in nodes["nodes"]}

    structure_report = {
        "timdr_breaks": timdr["problems"] if timdr["status"] == "warning" else [],
        "gia_overload": gia["discarded_fields"],
        "fieldcore_tension": {
            market: info["status"] for market, info in field["markets"].items()
        },
        "core_nodes_weakness": {
            name: result["weaknesses"] for name, result in node_analysis.items()
        },
    }
    risk = analyze_risk(structure_report)

    # patrz "UWAGA O ZAKRESIE" w naglowku modulu
    n_problem_dims = int(timdr["status"] == "warning") + int(field["status"] == "warning")
    level = _LEVELS[n_problem_dims]

    return {
        "timdr": timdr,
        "gia": gia,
        "fieldcore": field,
        "nodes": node_analysis,
        "risk": risk,
        "level": level,
        "hint": "Walidacja GSF zakończona — struktura pola została przeanalizowana.",
    }
