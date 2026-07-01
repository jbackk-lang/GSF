import json

def load_core_nodes(schema_path="GSF/CORE-NODES/nodes.json"):
    with open(schema_path, "r") as f:
        return json.load(f)

def analyze_node(node_data):
    strengths = node_data["strengths"]
    weaknesses = node_data["weaknesses"]

    return {
        "status": "ok",
        "strengths": strengths,
        "weaknesses": weaknesses,
        "hint": "Rdzeń pola zmapowany — tensor może zostać zdeformowany zgodnie z FIELDCORE."
    }
