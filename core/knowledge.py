import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1] / "data"
def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))
def catalog():
    return load("menu.json")
def products():
    m = catalog()
    return m["productos"] + m["bebidas"] + m["complementos"]
def product_by_id(pid):
    return next((x for x in products() if x["id"] == pid), None)
