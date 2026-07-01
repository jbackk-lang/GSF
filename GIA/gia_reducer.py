import json

def gia_reduce(model, schema_path="GSF/GIA/gia_map.json"):
    with open(schema_path, "r") as f:
        schema = json.load(f)

    core = schema["core_fields"]
    reduced = {}

    for field in core:
        if field in model:
            reduced[field] = model[field]

    return {
        "status": "ok",
        "reduced_model": reduced,
        "hint": "Model został zredukowany do pól sterujących zgodnie z GIA."
    }
