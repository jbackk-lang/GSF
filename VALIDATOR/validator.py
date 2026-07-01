import json

from GSF.TIMDR.validator_timdr import validate_timdr_continuity
from GSF.GIA.gia_reducer import gia_reduce
from GSF.FIELDCORE.fieldcore_tensor import fieldcore_tensor
from GSF.CORE-NODES.core_nodes import load_core_nodes, analyze_node

def validate_gsf(data):
    timdr = validate_timdr_continuity(data)
    gia = gia_reduce(data)
    field = fieldcore_tensor(data)
    nodes = load_core_nodes()

    node_analysis = {name: analyze_node(nodes["nodes"][name]) for name in nodes["nodes"]}

    return {
        "timdr": timdr,
        "gia": gia,
        "fieldcore": field,
        "nodes": node_analysis,
        "hint": "Walidacja GSF zakończona — struktura pola została przeanalizowana."
    }
